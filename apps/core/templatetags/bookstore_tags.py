from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter."""
    return value.split(delimiter)


@register.filter
def get_first(value):
    """Get first element of a list."""
    if isinstance(value, (list, tuple)) and len(value) > 0:
        return value[0]
    return value


@register.filter
def get_last(value):
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
