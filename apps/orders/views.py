from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction, models
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
from .vnpay import vnpay
from apps.cart.views import get_or_create_cart
from apps.catalog.models import Book
from .models import Order, OrderItem, Coupon
from .forms import CheckoutForm


@login_required
def checkout(request):
    """Checkout page - create an order from cart."""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('book').all()

    if not items.exists():
        messages.warning(request, _('Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi thanh toán.'))
        return redirect('cart:cart_detail')

    # Validate stock
    for item in items:
        if item.quantity > item.book.stock:
            messages.error(
                request,
                _(f'"{item.book.title}" chỉ còn {item.book.stock} sản phẩm.')
            )
            return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            return _process_checkout(request, form, cart, items)
    else:
        # Pre-fill with default address
        initial = {}
        default_addr = request.user.addresses.filter(is_default=True).first()
        if default_addr:
            initial['saved_address'] = default_addr.pk
        form = CheckoutForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
    }
    return render(request, 'orders/checkout.html', context)


@transaction.atomic
def _process_checkout(request, form, cart, items):
    """Process the checkout and create the order."""
    # Re-validate stock with lock to prevent race conditions
    book_ids = [item.book.pk for item in items]
    books = Book.objects.filter(pk__in=book_ids).select_for_update()
    book_dict = {book.pk: book for book in books}

    for item in items:
        book = book_dict.get(item.book.pk)
        if not book or book.stock < item.quantity:
            transaction.set_rollback(True)
            messages.error(request, _(f'"{item.book.title}" chỉ còn {book.stock if book else 0} sản phẩm.'))
            return redirect('cart:cart_detail')
    # Determine shipping address
    saved_address = form.cleaned_data.get('saved_address')
    if saved_address:
        shipping_name = saved_address.full_name
        shipping_phone = saved_address.phone
        shipping_address = saved_address.address_line
        shipping_ward = saved_address.ward
        shipping_district = saved_address.district
        shipping_city = saved_address.city
    else:
        shipping_name = form.cleaned_data['shipping_name']
        shipping_phone = form.cleaned_data['shipping_phone']
        shipping_address = form.cleaned_data['shipping_address']
        shipping_ward = form.cleaned_data.get('shipping_ward', '')
        shipping_district = form.cleaned_data['shipping_district']
        shipping_city = form.cleaned_data['shipping_city']

    # Calculate totals
    subtotal = cart.subtotal
    shipping_fee = _calculate_shipping(subtotal)
    discount_amount = 0
    coupon = None
    coupon_code = form.cleaned_data.get('coupon_code', '').strip()

    if coupon_code:
        try:
            coupon = Coupon.objects.select_for_update().get(code__iexact=coupon_code)
            if coupon.is_valid:
                discount_amount = coupon.calculate_discount(subtotal)
            else:
                messages.warning(request, _('Mã giảm giá không hợp lệ hoặc đã hết hạn.'))
                coupon = None
                coupon_code = ''
        except Coupon.DoesNotExist:
            messages.warning(request, _('Mã giảm giá không tồn tại.'))
            coupon_code = ''

    total = subtotal + shipping_fee - discount_amount

    # Create order
    order = Order.objects.create(
        user=request.user,
        shipping_name=shipping_name,
        shipping_phone=shipping_phone,
        shipping_address=shipping_address,
        shipping_ward=shipping_ward,
        shipping_district=shipping_district,
        shipping_city=shipping_city,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        total=total,
        coupon=coupon,
        coupon_code=coupon_code,
        payment_method=form.cleaned_data['payment_method'],
        note=form.cleaned_data.get('note', ''),
    )

    # Create order items and update stock
    for item in items:
        OrderItem.objects.create(
            order=order,
            book=item.book,
            book_title=item.book.title,
            book_price=item.book.price,
            book_cover=item.book.cover_image.url if item.book.cover_image else '',
            quantity=item.quantity,
        )
        # Update stock and sold count directly on the locked book instance
        book = book_dict[item.book.pk]
        book.stock -= item.quantity
        book.sold_count += item.quantity
        book.save(update_fields=['stock', 'sold_count'])

    # Update coupon usage
    if coupon:
        coupon.used_count = models.F('used_count') + 1
        coupon.save(update_fields=['used_count'])

    # Clear cart
    cart.clear()

    # Send confirmation email
    subject = f'Xác nhận đơn hàng #{order.order_number}'
    html_message = render_to_string('orders/email/order_confirmation.html', {'order': order})
    plain_message = strip_tags(html_message)
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Failed to send order confirmation email for order {order.order_number}: {str(e)}')

    if order.payment_method == 'vnpay':
        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
        vnp.requestData['vnp_Amount'] = str(int(order.total) * 100)
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = order.order_number
        vnp.requestData['vnp_OrderInfo'] = f'Thanh toan don hang {order.order_number}'
        vnp.requestData['vnp_OrderType'] = 'billpayment'
        vnp.requestData['vnp_Locale'] = 'vn'
        vnp.requestData['vnp_CreateDate'] = timezone.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = request.META.get('REMOTE_ADDR', '127.0.0.1')
        vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_URL, settings.VNPAY_HASH_SECRET_KEY)
        return redirect(vnpay_payment_url)

    messages.success(request, _('Đặt hàng thành công! Cảm ơn bạn đã mua hàng.'))
    return redirect('orders:order_success', order_number=order.order_number)


def _calculate_shipping(subtotal):
    """Calculate shipping fee based on order subtotal."""
    # Free shipping for orders over 300,000₫
    if subtotal >= 300000:
        return 0
    return 30000  # Default shipping fee


@login_required
def order_success(request, order_number):
    """Order success/confirmation page."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_number=order_number, user=request.user,
    )
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_detail(request, order_number):
    """Order detail page."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__book'),
        order_number=order_number, user=request.user,
    )
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_cancel(request, order_number):
    """Cancel an order."""
    if request.method == 'POST':
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), order_number=order_number, user=request.user)

            if not order.can_cancel:
                messages.error(request, _('Không thể hủy đơn hàng này.'))
                return redirect('orders:order_detail', order_number=order_number)

            # Restore stock
            for item in order.items.all():
                if item.book:
                    Book.objects.filter(pk=item.book.pk).update(
                        stock=models.F('stock') + item.quantity,
                        sold_count=models.F('sold_count') - item.quantity,
                    )
            # Update order status
            order.status = Order.Status.CANCELLED
            order.cancelled_at = timezone.now()
            order.save(update_fields=['status', 'cancelled_at', 'updated_at'])

        messages.success(request, _('Đã hủy đơn hàng thành công.'))

    return redirect('orders:order_detail', order_number=order_number)

def vnpay_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_number = inputData.get('vnp_TxnRef')
        amount = int(inputData.get('vnp_Amount', 0)) / 100
        order_desc = inputData.get('vnp_OrderInfo')
        vnp_TransactionNo = inputData.get('vnp_TransactionNo')
        vnp_ResponseCode = inputData.get('vnp_ResponseCode')
        vnp_TmnCode = inputData.get('vnp_TmnCode')
        vnp_PayDate = inputData.get('vnp_PayDate')
        vnp_BankCode = inputData.get('vnp_BankCode')
        vnp_CardType = inputData.get('vnp_CardType')
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                # Success
                try:
                    order = Order.objects.get(order_number=order_number)
                    order.payment_status = Order.PaymentStatus.PAID
                    order.save(update_fields=['payment_status'])
                    messages.success(request, _('Thanh toán VNPay thành công!'))
                    return redirect('orders:order_success', order_number=order.order_number)
                except Order.DoesNotExist:
                    messages.error(request, _('Đơn hàng không tồn tại.'))
            else:
                messages.error(request, _('Thanh toán lỗi hoặc bị hủy.'))
        else:
            messages.error(request, _('Chữ ký không hợp lệ.'))
    else:
        messages.error(request, _('Không có dữ liệu trả về.'))
    return redirect('core:home')
