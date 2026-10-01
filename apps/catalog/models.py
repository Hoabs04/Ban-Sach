from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from PIL import Image
import uuid


class Category(models.Model):
    """Book category with support for hierarchical structure."""

    name = models.CharField(_('Tên danh mục'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, blank=True)
    description = models.TextField(_('Mô tả'), blank=True)
    image = models.ImageField(_('Ảnh'), upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='children', blank=True, null=True,
        verbose_name=_('Danh mục cha'),
    )
    is_active = models.BooleanField(_('Đang hoạt động'), default=True)
    order = models.IntegerField(_('Thứ tự'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Danh mục')
        verbose_name_plural = _('Danh mục')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

    @property
    def book_count(self):
        return self.books.filter(is_active=True).count()


class Author(models.Model):
    """Book author."""

    name = models.CharField(_('Tên tác giả'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True, blank=True)
    bio = models.TextField(_('Tiểu sử'), blank=True)
    photo = models.ImageField(_('Ảnh'), upload_to='authors/', blank=True, null=True)
    website = models.URLField(_('Website'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Tác giả')
        verbose_name_plural = _('Tác giả')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:author_detail', kwargs={'slug': self.slug})


class Publisher(models.Model):
    """Book publisher."""

    name = models.CharField(_('Tên nhà xuất bản'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True, blank=True)
    description = models.TextField(_('Mô tả'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='publishers/', blank=True, null=True)
    website = models.URLField(_('Website'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Nhà xuất bản')
        verbose_name_plural = _('Nhà xuất bản')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Book(models.Model):
    """Main book/product model."""

    class Format(models.TextChoices):
        PAPERBACK = 'paperback', _('Bìa mềm')
        HARDCOVER = 'hardcover', _('Bìa cứng')
        EBOOK = 'ebook', _('Sách điện tử')

    # Basic info
    title = models.CharField(_('Tên sách'), max_length=500)
    slug = models.SlugField(_('Slug'), max_length=500, unique=True, blank=True)
    sku = models.CharField(_('Mã sách'), max_length=50, unique=True, blank=True)
    isbn = models.CharField(_('ISBN'), max_length=20, blank=True, db_index=True)
    description = models.TextField(_('Mô tả'), blank=True)
    short_description = models.CharField(_('Mô tả ngắn'), max_length=500, blank=True)

    # Relationships
    categories = models.ManyToManyField(
        Category, related_name='books',
        verbose_name=_('Danh mục'), blank=True,
    )
    authors = models.ManyToManyField(
        Author, related_name='books',
        verbose_name=_('Tác giả'), blank=True,
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL,
        related_name='books', null=True, blank=True,
        verbose_name=_('Nhà xuất bản'),
    )

    # Pricing
    price = models.DecimalField(
        _('Giá bán'), max_digits=12, decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    original_price = models.DecimalField(
        _('Giá gốc'), max_digits=12, decimal_places=0,
        blank=True, null=True,
        validators=[MinValueValidator(0)],
    )

    # Book details
    format = models.CharField(
        _('Định dạng'), max_length=20,
        choices=Format.choices, default=Format.PAPERBACK,
    )
    pages = models.PositiveIntegerField(_('Số trang'), blank=True, null=True)
    publication_year = models.PositiveIntegerField(_('Năm xuất bản'), blank=True, null=True)
    language = models.CharField(_('Ngôn ngữ'), max_length=50, default='Tiếng Việt')
    weight = models.PositiveIntegerField(_('Trọng lượng (gram)'), blank=True, null=True)
    dimensions = models.CharField(_('Kích thước'), max_length=100, blank=True)

    # Cover image
    cover_image = models.ImageField(
        _('Ảnh bìa'), upload_to='books/covers/',
        blank=True, null=True,
    )

    # Inventory
    stock = models.PositiveIntegerField(_('Số lượng tồn kho'), default=0)
    low_stock_threshold = models.PositiveIntegerField(_('Ngưỡng tồn kho thấp'), default=5)

    # Stats
    sold_count = models.PositiveIntegerField(_('Số lượng đã bán'), default=0)
    view_count = models.PositiveIntegerField(_('Số lượt xem'), default=0)

    # Status
    is_active = models.BooleanField(_('Đang bán'), default=True)
    is_featured = models.BooleanField(_('Nổi bật'), default=False)

    # Timestamps
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Sách')
        verbose_name_plural = _('Sách')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['isbn']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-sold_count']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            # Ensure uniqueness
            if Book.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        if not self.sku:
            self.sku = f"BK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

        # Image optimization
        if self.cover_image:
            try:
                img = Image.open(self.cover_image.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.cover_image.path, quality=85, optimize=True)
            except Exception:
                pass
    def get_absolute_url(self):
        return reverse('catalog:book_detail', kwargs={'slug': self.slug})

    @property
    def discount_percent(self):
        """Calculate discount percentage."""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    @property
    def average_rating(self):
        """Get average rating from reviews."""
        if hasattr(self, 'approved_reviews'):
            reviews = self.approved_reviews
            if reviews:
                return round(sum(r.rating for r in reviews) / len(reviews), 1)
            return 0
            
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def review_count(self):
        if hasattr(self, 'approved_reviews'):
            return len(self.approved_reviews)
        return self.reviews.filter(is_approved=True).count()

    @property
    def authors_display(self):
        """Comma-separated author names."""
        return ', '.join(a.name for a in self.authors.all())


class BookImage(models.Model):
    """Additional images for a book."""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Sách'),
    )
    image = models.ImageField(_('Ảnh'), upload_to='books/images/')
    alt_text = models.CharField(_('Mô tả ảnh'), max_length=255, blank=True)
    order = models.IntegerField(_('Thứ tự'), default=0)

    class Meta:
        verbose_name = _('Ảnh sách')
        verbose_name_plural = _('Ảnh sách')
        ordering = ['order']

    def __str__(self):
        return f"Ảnh {self.order} - {self.book.title}"


class Review(models.Model):
    """Book review/rating by a customer."""

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Sách'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Người dùng'),
    )
    rating = models.IntegerField(
        _('Đánh giá'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    title = models.CharField(_('Tiêu đề'), max_length=255, blank=True)
    comment = models.TextField(_('Nhận xét'))
    is_approved = models.BooleanField(_('Đã duyệt'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Đánh giá')
        verbose_name_plural = _('Đánh giá')
        ordering = ['-created_at']
        unique_together = ['book', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}: {self.rating}★"
