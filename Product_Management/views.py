from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'Product_Management/index.html', {
        'products': products,
        'categories': categories,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'Product_Management/detail.html', {'product': product})



def product_list(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, 'Product_Management/index.html', {
        'products': products,
        'categories': categories,
        'search_query': query,
    })