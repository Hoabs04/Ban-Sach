from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User, Address


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'avatar', 'receive_newsletter']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Họ'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Tên'}),
            'phone': forms.TextInput(attrs={'placeholder': '0123 456 789'}),
        }


class AddressForm(forms.ModelForm):
    """Form for creating/editing addresses."""

    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'ward', 'district', 'city', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nguyễn Văn A'}),
            'phone': forms.TextInput(attrs={'placeholder': '0123 456 789'}),
            'address_line': forms.TextInput(attrs={'placeholder': 'Số nhà, tên đường'}),
            'ward': forms.TextInput(attrs={'placeholder': 'Phường/Xã'}),
            'district': forms.TextInput(attrs={'placeholder': 'Quận/Huyện'}),
            'city': forms.TextInput(attrs={'placeholder': 'Tỉnh/Thành phố'}),
        }
