from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FunCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon_name = models.CharField(max_length=50, default='fa-shield-halved')
    theme_color = models.CharField(max_length=20, default='indigo')

    def __str__(self):
        return self.name


class KidsProduct(models.Model):
    category = models.ForeignKey(FunCategory, on_delete=models.CASCADE, related_name='kids_products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    stat_boost = models.CharField(max_length=50, default='+10 XP')
    reward_coins = models.PositiveIntegerField(default=10)
    is_sugar_free = models.BooleanField(default=False)

    def __str__(self):
        return self.name