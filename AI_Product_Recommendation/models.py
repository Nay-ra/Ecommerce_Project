# Create your models here.
from django.db import models
from django.conf import settings
from Product_Management.models import Product

class UserInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)  # e.g., 'view', 'add_to_cart', 'purchase'
    timestamp = models.DateTimeField(auto_now_add=True)