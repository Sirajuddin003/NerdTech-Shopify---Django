from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

def cart_item_count(request):
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            from .views import _cart_id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_count = cart_items.count()
    except ObjectDoesNotExist:
        cart_count = 0

    return {'cart_count': cart_count}
