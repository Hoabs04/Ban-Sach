from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Book


class Cart(models.Model):
    """Shopping cart - linked to user or session."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cart', null=True, blank=True,
        verbose_name=_('Người dùng'),
    )
    session_key = models.CharField(
        _('Session key'), max_length=255,
        null=True, blank=True, db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Giỏ hàng')
        verbose_name_plural = _('Giỏ hàng')

    def __str__(self):
        if self.user:
            return f"Giỏ hàng của {self.user.username}"
        return f"Giỏ hàng (session: {self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def total(self):
        return self.subtotal

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    """Individual item in a shopping cart."""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Giỏ hàng'),
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        verbose_name=_('Sách'),
    )
    quantity = models.PositiveIntegerField(_('Số lượng'), default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sản phẩm trong giỏ')
        verbose_name_plural = _('Sản phẩm trong giỏ')
        unique_together = ['cart', 'book']

    def __str__(self):
        return f"{self.quantity}x {self.book.title}"

    @property
    def line_total(self):
        return self.book.price * self.quantity
