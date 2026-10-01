from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Avg, Count, Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Book, Category, Author, Review


def book_list(request):
    """List all books with filtering and sorting."""
    review_prefetch = Prefetch('reviews', queryset=Review.objects.filter(is_approved=True), to_attr='approved_reviews')
    books = Book.objects.filter(is_active=True).select_related(
        'publisher'
    ).prefetch_related('authors', 'categories', review_prefetch)

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        books = books.filter(categories__slug=category_slug)

    # Author filter
    author_slug = request.GET.get('author')
    if author_slug:
        books = books.filter(authors__slug=author_slug)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try:
        if min_price:
            books = books.filter(price__gte=int(min_price))
        if max_price:
            books = books.filter(price__lte=int(max_price))
    except ValueError:
        pass

    # Format filter
    book_format = request.GET.get('format')
    if book_format:
        books = books.filter(format=book_format)

    # Rating filter
    min_rating = request.GET.get('rating')
    try:
        if min_rating:
            min_rating_val = int(min_rating)
            books = books.annotate(
                avg_rating=Avg('reviews__rating', filter=models.Q(reviews__is_approved=True))
            ).filter(avg_rating__gte=min_rating_val)
    except ValueError:
        pass

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'bestseller': '-sold_count',
        'name': 'title',
        'rating': '-avg_rating_sort',
    }
    order = sort_options.get(sort, '-created_at')
    if sort == 'rating':
        books = books.annotate(
            avg_rating_sort=Avg('reviews__rating', filter=models.Q(reviews__is_approved=True))
        ).order_by(order).distinct()
    else:
        books = books.order_by(order).distinct()

    # Pagination
    paginator = Paginator(books, getattr(settings, 'ITEMS_PER_PAGE', 12))
    page = request.GET.get('page')
    books = paginator.get_page(page)

    # Categories for sidebar filter
    categories = Category.objects.filter(
        is_active=True, parent__isnull=True
    ).prefetch_related('children').annotate(
        active_books=Count('books', filter=Q(books__is_active=True))
    )

    context = {
        'books': books,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort,
    }
    return render(request, 'catalog/book_list.html', context)


def book_search(request):
    """Search books by title, author, ISBN."""
    query = request.GET.get('q', '').strip()
    books = Book.objects.filter(is_active=True)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(publisher__name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'bestseller': '-sold_count',
        'name': 'title',
    }
    order = sort_options.get(sort, '-created_at')
    review_prefetch = Prefetch('reviews', queryset=Review.objects.filter(is_approved=True), to_attr='approved_reviews')
    books = books.select_related('publisher').prefetch_related('authors', review_prefetch).order_by(order)

    # Pagination
    paginator = Paginator(books, getattr(settings, 'ITEMS_PER_PAGE', 12))
    page = request.GET.get('page')
    books = paginator.get_page(page)

    context = {
        'books': books,
        'query': query,
        'current_sort': sort,
    }
    return render(request, 'catalog/search_results.html', context)


def book_detail(request, slug):
    """Book detail page."""
    book = get_object_or_404(
        Book.objects.select_related('publisher').prefetch_related(
            'authors', 'categories', 'images',
            'reviews__user',
        ),
        slug=slug, is_active=True,
    )

    # Increment view count
    Book.objects.filter(pk=book.pk).update(view_count=models.F('view_count') + 1)
    book.view_count += 1

    # Related books (same categories)
    review_prefetch = Prefetch('reviews', queryset=Review.objects.filter(is_approved=True), to_attr='approved_reviews')
    related_books = Book.objects.filter(
        is_active=True,
        categories__in=book.categories.all(),
    ).exclude(pk=book.pk).select_related('publisher').prefetch_related(
        'authors', 'categories', review_prefetch
    ).distinct()[:4]

    # Check if user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(book=book, user=request.user).first()

    # Reviews
    reviews = book.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')

    context = {
        'book': book,
        'related_books': related_books,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'catalog/book_detail.html', context)


def category_detail(request, slug):
    """Category page with books."""
    category = get_object_or_404(Category, slug=slug, is_active=True)

    # Get books in this category and its children
    category_ids = [category.pk]
    for child in category.children.filter(is_active=True):
        category_ids.append(child.pk)

    review_prefetch = Prefetch('reviews', queryset=Review.objects.filter(is_approved=True), to_attr='approved_reviews')
    books = Book.objects.filter(
        is_active=True, categories__id__in=category_ids
    ).select_related('publisher').prefetch_related('authors', review_prefetch).distinct()

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'bestseller': '-sold_count',
        'name': 'title',
    }
    order = sort_options.get(sort, '-created_at')
    books = books.order_by(order)

    # Pagination
    paginator = Paginator(books, getattr(settings, 'ITEMS_PER_PAGE', 12))
    page = request.GET.get('page')
    books = paginator.get_page(page)

    # Subcategories
    subcategories = category.children.filter(is_active=True)

    context = {
        'category': category,
        'books': books,
        'subcategories': subcategories,
        'current_sort': sort,
    }
    return render(request, 'catalog/category_detail.html', context)


def author_detail(request, slug):
    """Author page with their books."""
    author = get_object_or_404(Author, slug=slug)
    books = author.books.filter(is_active=True).select_related(
        'publisher'
    ).prefetch_related('authors')

    # Pagination
    paginator = Paginator(books, getattr(settings, 'ITEMS_PER_PAGE', 12))
    page = request.GET.get('page')
    books = paginator.get_page(page)

    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'catalog/author_detail.html', context)


@login_required
def add_review(request, slug):
    """Add a review for a book."""
    book = get_object_or_404(Book, slug=slug, is_active=True)

    if request.method == 'POST':
        # Check if user already reviewed
        if Review.objects.filter(book=book, user=request.user).exists():
            messages.warning(request, _('Bạn đã đánh giá sách này rồi.'))
            return redirect('catalog:book_detail', slug=slug)

        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')

        if rating and comment:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError()
            except ValueError:
                messages.error(request, _('Điểm đánh giá không hợp lệ.'))
                return redirect('catalog:book_detail', slug=slug)

            Review.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                title=title,
                comment=comment,
            )
            messages.success(request, _('Cảm ơn bạn đã đánh giá!'))
        else:
            messages.error(request, _('Vui lòng nhập đầy đủ thông tin đánh giá.'))

    return redirect('catalog:book_detail', slug=slug)
