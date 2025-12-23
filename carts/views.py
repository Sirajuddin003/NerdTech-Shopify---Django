from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
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
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        ex_var_list = []
        id_list = []

        for item in cart_items:
            ex_var_list.append(list(item.variations.all()))
            id_list.append(item.id)

        # SAME product + SAME variations
        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.quantity += 1
            cart_item.save()

        # SAME product + DIFFERENT variations → NEW ROW
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.variations.add(*product_variation)
            cart_item.save()

    # Product not in cart at all
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.variations.add(*product_variation)
        cart_item.save()

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

def increase_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
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
