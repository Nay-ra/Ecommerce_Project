from django.urls import path
from . import views

app_name = 'AI_Product_Recommendation'

urlpatterns = [
    path('', views.recommendation_view, name='recommendations'),
]