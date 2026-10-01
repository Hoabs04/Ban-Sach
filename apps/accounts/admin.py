from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    fields = ('full_name', 'phone', 'address_line', 'ward', 'district', 'city', 'is_default')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    inlines = [AddressInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Thông tin bổ sung'), {
            'fields': ('phone', 'avatar', 'role', 'date_of_birth', 'receive_newsletter'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Thông tin bổ sung'), {
            'fields': ('email', 'phone', 'role'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'district', 'city', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('full_name', 'phone', 'address_line', 'city')
