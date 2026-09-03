from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Automatically generates slug as you type the name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock', 'is_available', 'created_at']
    list_filter = ['is_available', 'category']
    list_editable = ['price', 'stock', 'is_available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}