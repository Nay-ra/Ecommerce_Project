from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Product_Management.models import Product

def get_cart(session):
    return session.get('cart', {})

def cart_detail(request):
    cart = get_cart(request.session)
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': item_total,
        })

    return render(request, 'Shopping_Cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    str_id = str(product_id)
    cart[str_id] = cart.get(str_id, 0) + 1
    
    request.session['cart'] = cart
    request.session.modified = True  # Ensures session saves
    messages.success(request, f'Added {product.name} to cart.')
    return redirect('Shopping_Cart:cart_detail')

def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        str_id = str(item_id)
        
        if quantity > 0:
            cart[str_id] = quantity
        else:
            cart.pop(str_id, None)
            
        request.session['cart'] = cart
        request.session.modified = True  # Ensures session saves
        messages.info(request, 'Cart updated.')
    return redirect('Shopping_Cart:cart_detail')

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    str_id = str(item_id)
    if str_id in cart:
        del cart[str_id]
        request.session['cart'] = cart
        request.session.modified = True  # Ensures session saves
        messages.info(request, 'Item removed from cart.')
    return redirect('Shopping_Cart:cart_detail')