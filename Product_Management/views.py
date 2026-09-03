from django.shortcuts import render
from .models import Product, Category

def product_list(request):
    # Retrieve all products (or filter by stock > 0 if preferred: stock__gt=0)
    products = Product.objects.all()
    categories = Category.objects.all()
    
    return render(request, 'Product_Management/index.html', {
        'products': products,
        'categories': categories,
    })