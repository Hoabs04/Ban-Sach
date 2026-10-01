from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter."""
    return value.split(delimiter)


@register.filter
def first(value):
    """Get first element of a list."""
    if isinstance(value, (list, tuple)) and len(value) > 0:
        return value[0]
    return value


@register.filter
def last(value):
    """Get last element of a list."""
    if isinstance(value, (list, tuple)) and len(value) > 0:
        return value[-1]
    return value


@register.filter
def currency_vnd(value):
    """Format number as Vietnamese currency."""
    try:
        return f"{int(value):,}₫".replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter
def star_range(value):
    """Generate a range for star rating display."""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)


@register.simple_tag
def query_string(request, **kwargs):
    """Build query string preserving existing params."""
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()
