from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )

    return redirect('cart')
 

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart,
            id=cart_item_id
        )

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart,
            id=cart_item_id
        )
        cart_item.delete()

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect('cart')


def cart(request):
    cart = None
    cart_items = []
    total = 0
    quantity = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        pass

    for item in cart_items:
        total += item.product.price * item.quantity
        quantity += item.quantity

    tax = (1 * total)/100
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)
