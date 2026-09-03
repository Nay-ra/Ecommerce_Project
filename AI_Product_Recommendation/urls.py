from django.urls import path
from . import views

app_name = 'AI_Product_Recommendation'

urlpatterns = [
    path('api/recommendations/<int:product_id>/', views.product_recommendations_api, name='recommendations_api'),
]