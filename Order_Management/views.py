from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Product_Management.models import Product
from django.db import transaction
from .models import Order, OrderItem

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('Shopping_Cart:cart_detail')

    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            
            # Check if requested quantity exceeds available stock
            if quantity > product.stock:
                messages.error(
                    request, 
                    f"Only {product.stock} units of {product.name} are available in stock."
                )
                return redirect('Shopping_Cart:cart_detail')

            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total,
            })
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        address = request.POST.get('address', '')

        # Use an atomic transaction to ensure order creation and stock reduction happen together
        with transaction.atomic():
            # 1. Create the primary Order instance
            order = Order.objects.create(
                user=request.user,
                total_amount=total_price,
                shipping_address=address,
                status='Pending'
            )

            # 2. Save OrderItems and update product stock
            for item in cart_items:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )

                # Deduct ordered quantity from product stock
                product.stock -= quantity
                product.save()

            # 3. Clear session cart
            request.session['cart'] = {}
            request.session.modified = True

        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('Order_Management:order_detail', order_id=order.id)

    return render(request, 'Order_Management/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def order_history(request):
    """Fetches all orders placed by the currently logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'Order_Management/order_history.html', {
        'orders': orders,
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    return render(request, 'Order_Management/order_detail.html', {
        'order': order,
        'order_items': order_items,
    })


@login_required
def cancel_order(request, order_id):
    """Allows a user to cancel a pending order and restores product stock."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Restrict cancellation to Pending or Processing orders
    if order.status not in ['Pending', 'Processing']:
        messages.error(request, f"Order #{order.id} cannot be canceled because it is already {order.status.lower()}.")
        return redirect('Order_Management:order_detail', order_id=order.id)

    if request.method == 'POST':
        with transaction.atomic():
            # 1. Return stock for each item in the order
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()

            # 2. Update order status
            order.status = 'Canceled'
            order.save()

        messages.success(request, f"Order #{order.id} has been canceled and stock restored.")
        return redirect('Order_Management:order_detail', order_id=order.id)

    return redirect('Order_Management:order_detail', order_id=order.id)