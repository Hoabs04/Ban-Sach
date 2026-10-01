import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.catalog.models import Book


class Coupon(models.Model):
    """Discount coupon."""

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Phần trăm')
        FIXED = 'fixed', _('Số tiền cố định')

    code = models.CharField(_('Mã giảm giá'), max_length=50, unique=True, db_index=True)
    description = models.CharField(_('Mô tả'), max_length=255, blank=True)
    discount_type = models.CharField(
        _('Loại giảm giá'), max_length=20,
        choices=DiscountType.choices, default=DiscountType.PERCENTAGE,
    )
    discount_value = models.DecimalField(
        _('Giá trị giảm'), max_digits=12, decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    min_order_amount = models.DecimalField(
        _('Giá trị đơn tối thiểu'), max_digits=12, decimal_places=0,
        default=0, validators=[MinValueValidator(0)],
    )
    max_discount = models.DecimalField(
        _('Giảm tối đa'), max_digits=12, decimal_places=0,
        blank=True, null=True,
    )
    usage_limit = models.PositiveIntegerField(_('Giới hạn sử dụng'), blank=True, null=True)
    used_count = models.PositiveIntegerField(_('Đã sử dụng'), default=0)
    is_active = models.BooleanField(_('Đang hoạt động'), default=True)
    valid_from = models.DateTimeField(_('Có hiệu lực từ'))
    valid_to = models.DateTimeField(_('Hết hạn'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mã giảm giá')
        verbose_name_plural = _('Mã giảm giá')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, order_total):
        """Calculate the discount amount for a given order total."""
        if order_total < self.min_order_amount:
            return 0

        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = order_total * self.discount_value / 100
        else:
            discount = self.discount_value

        if self.max_discount:
            discount = min(discount, self.max_discount)

        return min(discount, order_total)


class Order(models.Model):
    """Customer order."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Chờ xác nhận')
        CONFIRMED = 'confirmed', _('Đã xác nhận')
        PACKING = 'packing', _('Đang đóng gói')
        SHIPPING = 'shipping', _('Đang giao')
        DELIVERED = 'delivered', _('Đã giao')
        CANCELLED = 'cancelled', _('Đã hủy')

    class PaymentMethod(models.TextChoices):
        COD = 'cod', _('Thanh toán khi nhận hàng')
        BANK_TRANSFER = 'bank_transfer', _('Chuyển khoản ngân hàng')
        VNPAY = 'vnpay', _('Thanh toán qua VNPay')

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Chưa thanh toán')
        PAID = 'paid', _('Đã thanh toán')
        REFUNDED = 'refunded', _('Đã hoàn tiền')

    # Order identifiers
    order_number = models.CharField(
        _('Mã đơn hàng'), max_length=20,
        unique=True, editable=False, db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='orders', null=True,
        verbose_name=_('Khách hàng'),
    )

    # Shipping address (snapshot at order time)
    shipping_name = models.CharField(_('Người nhận'), max_length=255)
    shipping_phone = models.CharField(_('SĐT người nhận'), max_length=15)
    shipping_address = models.CharField(_('Địa chỉ giao hàng'), max_length=500)
    shipping_ward = models.CharField(_('Phường/Xã'), max_length=100, blank=True)
    shipping_district = models.CharField(_('Quận/Huyện'), max_length=100)
    shipping_city = models.CharField(_('Tỉnh/Thành phố'), max_length=100)

    # Pricing
    subtotal = models.DecimalField(
        _('Tạm tính'), max_digits=12, decimal_places=0, default=0,
    )
    shipping_fee = models.DecimalField(
        _('Phí vận chuyển'), max_digits=12, decimal_places=0, default=0,
    )
    discount_amount = models.DecimalField(
        _('Giảm giá'), max_digits=12, decimal_places=0, default=0,
    )
    total = models.DecimalField(
        _('Tổng cộng'), max_digits=12, decimal_places=0, default=0,
    )

    # Coupon
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Mã giảm giá'),
    )
    coupon_code = models.CharField(_('Mã coupon đã dùng'), max_length=50, blank=True)

    # Status
    status = models.CharField(
        _('Trạng thái'), max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )
    payment_method = models.CharField(
        _('Phương thức thanh toán'), max_length=20,
        choices=PaymentMethod.choices, default=PaymentMethod.COD,
    )
    payment_status = models.CharField(
        _('Trạng thái thanh toán'), max_length=20,
        choices=PaymentStatus.choices, default=PaymentStatus.PENDING,
    )

    # Notes
    note = models.TextField(_('Ghi chú'), blank=True)
    admin_note = models.TextField(_('Ghi chú nội bộ'), blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('Ngày đặt'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Cập nhật'), auto_now=True)
    confirmed_at = models.DateTimeField(_('Ngày xác nhận'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('Ngày giao'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Ngày nhận'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('Ngày hủy'), null=True, blank=True)

    class Meta:
        verbose_name = _('Đơn hàng')
        verbose_name_plural = _('Đơn hàng')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Đơn #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        """Generate a unique order number."""
        from django.utils import timezone
        prefix = timezone.now().strftime('%y%m%d')
        random_part = uuid.uuid4().hex[:6].upper()
        return f"DH{prefix}{random_part}"

    @property
    def full_shipping_address(self):
        parts = [self.shipping_address]
        if self.shipping_ward:
            parts.append(self.shipping_ward)
        parts.extend([self.shipping_district, self.shipping_city])
        return ', '.join(parts)

    @property
    def can_cancel(self):
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]

    @property
    def status_color(self):
        colors = {
            'pending': 'yellow',
            'confirmed': 'blue',
            'packing': 'indigo',
            'shipping': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
        }
        return colors.get(self.status, 'gray')


class OrderItem(models.Model):
    """Individual item in an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Đơn hàng'),
    )
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL,
        null=True, verbose_name=_('Sách'),
    )
    # Snapshot data at order time
    book_title = models.CharField(_('Tên sách'), max_length=500)
    book_price = models.DecimalField(_('Giá'), max_digits=12, decimal_places=0)
    book_cover = models.CharField(_('Ảnh bìa'), max_length=500, blank=True)
    quantity = models.PositiveIntegerField(_('Số lượng'), default=1)

    class Meta:
        verbose_name = _('Sản phẩm trong đơn')
        verbose_name_plural = _('Sản phẩm trong đơn')

    def __str__(self):
        return f"{self.quantity}x {self.book_title}"

    @property
    def line_total(self):
        return self.book_price * self.quantity
