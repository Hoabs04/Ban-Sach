from django import forms
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import Address
from .models import Order


class CheckoutForm(forms.Form):
    """Form for the checkout process."""

    # Address selection (for logged-in users with saved addresses)
    saved_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        label=_('Chọn địa chỉ đã lưu'),
        empty_label=_('— Nhập địa chỉ mới —'),
    )

    # New address fields
    shipping_name = forms.CharField(
        max_length=255, required=False,
        label=_('Họ và tên người nhận'),
        widget=forms.TextInput(attrs={'placeholder': 'Nguyễn Văn A'}),
    )
    shipping_phone = forms.CharField(
        max_length=15, required=False,
        label=_('Số điện thoại'),
        widget=forms.TextInput(attrs={'placeholder': '0123 456 789'}),
    )
    shipping_address = forms.CharField(
        max_length=500, required=False,
        label=_('Địa chỉ'),
        widget=forms.TextInput(attrs={'placeholder': 'Số nhà, tên đường'}),
    )
    shipping_ward = forms.CharField(
        max_length=100, required=False,
        label=_('Phường/Xã'),
    )
    shipping_district = forms.CharField(
        max_length=100, required=False,
        label=_('Quận/Huyện'),
    )
    shipping_city = forms.CharField(
        max_length=100, required=False,
        label=_('Tỉnh/Thành phố'),
    )

    # Payment
    payment_method = forms.ChoiceField(
        choices=Order.PaymentMethod.choices,
        label=_('Phương thức thanh toán'),
        initial=Order.PaymentMethod.COD,
    )

    # Coupon
    coupon_code = forms.CharField(
        max_length=50, required=False,
        label=_('Mã giảm giá'),
        widget=forms.TextInput(attrs={'placeholder': 'Nhập mã giảm giá'}),
    )

    # Note
    note = forms.CharField(
        required=False,
        label=_('Ghi chú'),
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ghi chú cho đơn hàng (ví dụ: giao giờ hành chính)',
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['saved_address'].queryset = user.addresses.all()

    def clean(self):
        cleaned_data = super().clean()
        saved_address = cleaned_data.get('saved_address')

        if not saved_address:
            # Require new address fields
            required_fields = [
                'shipping_name', 'shipping_phone',
                'shipping_address', 'shipping_district', 'shipping_city',
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('Trường này là bắt buộc.'))

        return cleaned_data
