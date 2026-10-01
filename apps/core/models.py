from django.db import models
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    name = models.CharField(_('Họ tên'), max_length=100)
    email = models.EmailField(_('Email'))
    message = models.TextField(_('Nội dung'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Tin nhắn liên hệ')
        verbose_name_plural = _('Tin nhắn liên hệ')

    def __str__(self):
        return f"{self.name} - {self.email}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(_('Email'), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Người đăng ký bản tin')
        verbose_name_plural = _('Người đăng ký bản tin')

    def __str__(self):
        return self.email
