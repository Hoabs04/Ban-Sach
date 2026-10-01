"""
Cart context processor to make cart item count available in all templates.
"""
from .models import Cart


def cart_count(request):
    """Add cart item count to template context."""
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
            else:
                cart = None

        if cart:
            count = cart.total_items
    except Exception:
        pass

    return {'cart_item_count': count}
