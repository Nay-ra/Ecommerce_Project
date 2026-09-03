from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from Product_Management.models import Product
from .models import CartItem
from .utils import get_or_create_user_cart

def cart_detail(request):
    """Displays items currently in the cart."""
    cart = get_or_create_user_cart(request)
    return render(request, 'Shopping_Cart/cart_detail.html', {'cart': cart})


@require_POST
def add_to_cart(request, product_id):
    """Adds a product to the cart with stock validation."""
    cart = get_or_create_user_cart(request)
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        requested_total = cart_item.quantity + quantity
        if requested_total > product.stock:
            messages.warning(request, f"Only {product.stock} units of '{product.name}' available in stock.")
            cart_item.quantity = product.stock
        else:
            cart_item.quantity = requested_total
        cart_item.save()
    else:
        if quantity > product.stock:
            messages.warning(request, f"Requested quantity exceeds stock. Added {product.stock} items instead.")
            cart_item.quantity = product.stock
            cart_item.save()

    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('Shopping_Cart:cart_detail')


@require_POST
def update_cart_quantity(request, item_id):
    """Updates item quantity in the cart."""
    cart = get_or_create_user_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, "Item removed from cart.")
    elif quantity > cart_item.product.stock:
        cart_item.quantity = cart_item.product.stock
        cart_item.save()
        messages.warning(request, f"Max available stock is {cart_item.product.stock}.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart updated.")

    return redirect('Shopping_Cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    """Removes an item completely from the cart."""
    cart = get_or_create_user_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('Shopping_Cart:cart_detail')