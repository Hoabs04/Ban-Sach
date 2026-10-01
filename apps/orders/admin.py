from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'book_title', 'book_price', 'quantity', 'line_total')
    fields = ('book', 'book_title', 'book_price', 'quantity', 'line_total')

    def line_total(self, obj):
        return f"{obj.line_total:,.0f}₫"
    line_total.short_description = _('Thành tiền')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'shipping_name',
        'total_display', 'status', 'payment_method',
        'payment_status', 'created_at',
    )
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'shipping_name', 'shipping_phone', 'user__username')
    readonly_fields = ('order_number', 'subtotal', 'total', 'discount_amount', 'created_at')
    inlines = [OrderItemInline]
    list_editable = ('status', 'payment_status')
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Thông tin đơn hàng'), {
            'fields': ('order_number', 'user', 'status', 'note', 'admin_note'),
        }),
        (_('Địa chỉ giao hàng'), {
            'fields': (
                'shipping_name', 'shipping_phone', 'shipping_address',
                'shipping_ward', 'shipping_district', 'shipping_city',
            ),
        }),
        (_('Thanh toán'), {
            'fields': (
                'payment_method', 'payment_status',
                'subtotal', 'shipping_fee', 'discount_amount', 'total',
                'coupon_code',
            ),
        }),
        (_('Thời gian'), {
            'fields': ('created_at', 'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at'),
            'classes': ('collapse',),
        }),
    )

    def total_display(self, obj):
        return f"{obj.total:,.0f}₫"
    total_display.short_description = _('Tổng cộng')

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'packing': '#6366f1',
            'shipping': '#8b5cf6',
            'delivered': '#10b981',
            'cancelled': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_status_display(),
        )
    status_badge.short_description = _('Trạng thái')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'discount_value',
        'used_count', 'usage_limit', 'is_active',
        'valid_from', 'valid_to',
    )
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
