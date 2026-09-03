from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from Shopping_Cart.utils import get_or_create_user_cart
from .models import Order, OrderItem

@login_required
def checkout(request):
    """
    Handles checkout processing using an atomic database transaction.
    Converts Cart items into OrderItems, updates inventory stock, and clears the cart.
    """
    cart = get_or_create_user_cart(request)
    cart_items = cart.items.select_related('product').all()

    # Reject checkout if cart is empty
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add items before checking out.")
        return redirect('Shopping_Cart:cart_detail')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '').strip()

        if not shipping_address:
            messages.error(request, "Shipping address is required to place an order.")
            return render(request, 'Order_Management/checkout.html', {
                'cart': cart,
                'cart_items': cart_items
            })

        try:
            with transaction.atomic():
                # Step 1: Stock pre-check & validation before altering data
                for item in cart_items:
                    product = item.product
                    if product.stock < item.quantity:
                        raise ValueError(
                            f"Sorry, '{product.name}' only has {product.stock} unit(s) left in stock."
                        )

                # Step 2: Create the Order instance
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    total_amount=cart.get_total_price,
                    status='Pending'
                )

                # Step 3: Convert CartItems to OrderItems & update product stock
                for item in cart_items:
                    product = item.product

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,  # Snapshot current price at time of order
                        quantity=item.quantity
                    )

                    # Deduct stock and update availability
                    product.stock -= item.quantity
                    if product.stock == 0:
                        product.is_available = False
                    product.save()

                # Step 4: Clear the user's cart items after successful creation
                cart_items.delete()

            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect('Order_Management:order_detail', order_id=order.id)

        except ValueError as e:
            # Handle out-of-stock validation error (Transaction rolls back automatically)
            messages.error(request, str(e))
            return redirect('Shopping_Cart:cart_detail')

        except Exception:
            # Handle unexpected database failures
            messages.error(request, "An error occurred while processing your order. Please try again.")
            return redirect('Shopping_Cart:cart_detail')

    # GET request: Display checkout confirmation form
    return render(request, 'Order_Management/checkout.html', {
        'cart': cart,
        'cart_items': cart_items
    })


@login_required
def order_detail(request, order_id):
    """Displays single order summary after successful placement."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'Order_Management/order_detail.html', {'order': order})


@login_required
def order_history(request):
    """Lists past orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Order_Management/order_history.html', {'orders': orders})