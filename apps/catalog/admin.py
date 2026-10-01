from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Author, Publisher, Book, BookImage, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'book_count', 'is_active', 'order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'cover_thumbnail', 'price_display',
        'stock', 'sold_count', 'is_active', 'is_featured',
    )
    list_filter = ('is_active', 'is_featured', 'format', 'categories', 'publication_year')
    search_fields = ('title', 'isbn', 'sku', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'authors')
    list_editable = ('is_active', 'is_featured')
    inlines = [BookImageInline]
    readonly_fields = ('sold_count', 'view_count', 'sku')

    fieldsets = (
        (_('Thông tin cơ bản'), {
            'fields': ('title', 'slug', 'sku', 'isbn', 'short_description', 'description'),
        }),
        (_('Phân loại'), {
            'fields': ('categories', 'authors', 'publisher'),
        }),
        (_('Giá & Kho'), {
            'fields': ('price', 'original_price', 'stock', 'low_stock_threshold'),
        }),
        (_('Chi tiết sách'), {
            'fields': ('format', 'pages', 'publication_year', 'language', 'weight', 'dimensions'),
        }),
        (_('Hình ảnh'), {
            'fields': ('cover_image',),
        }),
        (_('Trạng thái'), {
            'fields': ('is_active', 'is_featured', 'sold_count', 'view_count'),
        }),
    )

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:50px; border-radius:4px;" />',
                obj.cover_image.url,
            )
        return '—'
    cover_thumbnail.short_description = _('Ảnh bìa')

    def price_display(self, obj):
        price_str = f"{obj.price:,.0f}₫"
        if obj.original_price and obj.original_price > obj.price:
            return format_html(
                '<span style="text-decoration:line-through;color:#999;">{}</span> <b>{}</b>',
                f"{obj.original_price:,.0f}₫", price_str,
            )
        return price_str
    price_display.short_description = _('Giá')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('book__title', 'user__username', 'comment')
    list_editable = ('is_approved',)
