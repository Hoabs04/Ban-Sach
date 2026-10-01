"""
Context processors for site-wide template variables.
"""


def site_settings(request):
    """Add site-wide settings to template context."""
    return {
        'SITE_NAME': 'BookStore',
        'SITE_TAGLINE': 'Thế giới sách & truyện',
        'SITE_DESCRIPTION': 'Website bán sách và truyện trực tuyến hàng đầu Việt Nam',
        'CONTACT_EMAIL': 'contact@bookstore.vn',
        'CONTACT_PHONE': '0123 456 789',
    }
