from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model with email as the primary identifier."""

    class Role(models.TextChoices):
        CUSTOMER = 'customer', _('Khách hàng')
        STAFF = 'staff', _('Nhân viên')
        ADMIN = 'admin', _('Quản trị viên')

    email = models.EmailField(_('email'), unique=True)
    phone = models.CharField(_('Số điện thoại'), max_length=15, blank=True)
    avatar = models.ImageField(_('Ảnh đại diện'), upload_to='avatars/', blank=True, null=True)
    role = models.CharField(
        _('Vai trò'),
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    date_of_birth = models.DateField(_('Ngày sinh'), blank=True, null=True)
    receive_newsletter = models.BooleanField(_('Nhận bản tin'), default=True)
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class Address(models.Model):
    """Shipping/billing address for a user."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('Người dùng'),
    )
    full_name = models.CharField(_('Họ và tên'), max_length=255)
    phone = models.CharField(_('Số điện thoại'), max_length=15)
    address_line = models.CharField(_('Địa chỉ'), max_length=255)
    ward = models.CharField(_('Phường/Xã'), max_length=100, blank=True)
    district = models.CharField(_('Quận/Huyện'), max_length=100)
    city = models.CharField(_('Tỉnh/Thành phố'), max_length=100)
    is_default = models.BooleanField(_('Địa chỉ mặc định'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Địa chỉ')
        verbose_name_plural = _('Địa chỉ')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.address_line}, {self.district}, {self.city}"

    def save(self, *args, **kwargs):
        # If setting as default, unset other defaults
        if self.is_default:
            Address.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
