from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Book, Category, Review
from .models import ContactMessage, NewsletterSubscriber


def home(request):
    """Homepage with featured books and categories."""
    context = cache.get('home_page_context')
    
    if not context:
        review_prefetch = Prefetch('reviews', queryset=Review.objects.filter(is_approved=True), to_attr='approved_reviews')
        
        featured_books = list(Book.objects.filter(
            is_active=True, is_featured=True
        ).select_related('publisher').prefetch_related('authors', 'categories', review_prefetch)[:8])

        new_books = list(Book.objects.filter(
            is_active=True
        ).select_related('publisher').prefetch_related('authors', review_prefetch).order_by('-created_at')[:8])

        bestsellers = list(Book.objects.filter(
            is_active=True
        ).select_related('publisher').prefetch_related('authors', review_prefetch).order_by('-sold_count')[:8])

        categories = list(Category.objects.filter(
            parent__isnull=True, is_active=True
        ).prefetch_related('children')[:12])

        context = {
            'featured_books': featured_books,
            'new_books': new_books,
            'bestsellers': bestsellers,
            'categories': categories,
        }
        cache.set('home_page_context', context, 60 * 15) # 15 minutes

    return render(request, 'core/home.html', context)


def about(request):
    """About us page."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and email and message:
            try:
                validate_email(email)
                ContactMessage.objects.create(name=name, email=email, message=message)
                messages.success(request, _('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong thời gian sớm nhất.'))
            except ValidationError:
                messages.error(request, _('Vui lòng nhập địa chỉ email hợp lệ.'))
        else:
            messages.error(request, _('Vui lòng điền đầy đủ thông tin.'))
        return redirect('core:contact')
    return render(request, 'core/contact.html')

def newsletter_subscribe(request):
    """Newsletter subscription dummy view."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                validate_email(email)
                NewsletterSubscriber.objects.get_or_create(email=email)
                messages.success(request, _('Cảm ơn bạn đã đăng ký nhận bản tin!'))
            except ValidationError:
                messages.error(request, _('Vui lòng nhập địa chỉ email hợp lệ.'))
        else:
            messages.error(request, _('Vui lòng nhập địa chỉ email hợp lệ.'))
            
    next_url = request.META.get('HTTP_REFERER', 'core:home')
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
        next_url = '/'
    return redirect(next_url)


def shipping_policy(request):
    """Shipping policy page."""
    return render(request, 'core/shipping_policy.html')


def return_policy(request):
    """Return policy page."""
    return render(request, 'core/return_policy.html')


def terms(request):
    """Terms of service page."""
    return render(request, 'core/terms.html')
