from .models import Cart, CartItem
from Product_Management.models import Product

def get_or_create_user_cart(request):
    """
    Retrieves or creates an active Cart instance for either authenticated or anonymous users.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id, user=None).first()
            if not cart:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
    return cart


def merge_session_cart_to_user(user, session_cart_id):
    """
    Merges an anonymous session cart into a newly logged-in user's database cart.
    """
    if not session_cart_id:
        return

    try:
        session_cart = Cart.objects.get(id=session_cart_id, user=None)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in session_cart.items.all():
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            defaults={'quantity': item.quantity}
        )
        if not created:
            # Check stock limit before merging quantities
            new_qty = user_item.quantity + item.quantity
            user_item.quantity = min(new_qty, item.product.stock)
            user_item.save()

    # Delete temporary session cart
    session_cart.delete()