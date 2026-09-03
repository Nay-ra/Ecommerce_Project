from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Product_Management.urls')),
    path('auth/', include('User_Authentication.urls')),
    path('cart/', include('Shopping_Cart.urls')),
    path('orders/', include('Order_Management.urls')),
    path('recommendations/', include('AI_Product_Recommendation.urls')),
    path('products/', include('Product_Management.urls', namespace='Product_Management')),
]