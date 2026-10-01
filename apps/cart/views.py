from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from apps.catalog.models import Book
from .models import Cart, CartItem


def get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if exists
        if created or not cart.items.exists():
            session_key = request.session.session_key
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key).first()
                if session_cart and session_cart != cart:
                    for item in session_cart.items.all():
                        existing = cart.items.filter(book=item.book).first()
                        if existing:
                            existing.quantity += item.quantity
                            if existing.quantity > item.book.stock:
                                existing.quantity = item.book.stock
                            existing.save()
                        else:
                            if item.quantity > item.book.stock:
                                item.quantity = item.book.stock
                            item.cart = cart
                            item.save()
                    session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def cart_detail(request):
    """Display cart contents."""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('book').all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_add(request, book_id):
    """Add a book to the cart."""
    book = get_object_or_404(Book, pk=book_id, is_active=True)
    cart = get_or_create_cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, _('Số lượng không hợp lệ.'))
        return redirect('catalog:book_detail', slug=book.slug)

    if quantity < 1:
        messages.error(request, _('Số lượng không hợp lệ.'))
        return redirect('catalog:book_detail', slug=book.slug)

    # Check stock
    if quantity > book.stock:
        messages.error(request, _(f'Chỉ còn {book.stock} sản phẩm trong kho.'))
        return redirect('catalog:book_detail', slug=book.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, book=book,
        defaults={'quantity': quantity},
    )

    if not created:
        new_qty = cart_item.quantity + quantity
        if new_qty > book.stock:
            messages.error(request, _(f'Chỉ còn {book.stock} sản phẩm trong kho.'))
            return redirect('cart:cart_detail')
        cart_item.quantity = new_qty
        cart_item.save()

    messages.success(request, _(f'Đã thêm "{book.title}" vào giỏ hàng!'))

    # Redirect back or to cart
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        next_url = '/'
    return redirect(next_url)


@require_POST
def cart_update(request, item_id):
    """Update quantity of a cart item."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, _('Số lượng không hợp lệ.'))
        return redirect('cart:cart_detail')

    if quantity < 1:
        item.delete()
        messages.info(request, _('Đã xóa sản phẩm khỏi giỏ hàng.'))
    elif quantity > item.book.stock:
        messages.error(request, _(f'Chỉ còn {item.book.stock} sản phẩm trong kho.'))
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, _('Đã cập nhật giỏ hàng.'))

    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, item_id):
    """Remove an item from the cart."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.info(request, _('Đã xóa sản phẩm khỏi giỏ hàng.'))
    return redirect('cart:cart_detail')


@require_POST
def cart_clear(request):
    """Clear all items from the cart."""
    cart = get_or_create_cart(request)
    cart.clear()
    messages.info(request, _('Đã xóa toàn bộ giỏ hàng.'))
    return redirect('cart:cart_detail')
