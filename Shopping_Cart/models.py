from django.db import models
from django.conf import settings
from Product_Management.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.username if self.user else 'Anonymous'})"

    @property
    def get_total_price(self):
        """Calculates total cost of all items in the cart."""
        return sum(item.get_subtotal for item in self.items.all())

    @property
    def get_total_items(self):
        """Calculates total number of item units in the cart."""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def get_subtotal(self):
        """Calculates subtotal for this specific line item."""
        return self.product.price * self.quantity