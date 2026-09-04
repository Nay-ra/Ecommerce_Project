from django.urls import path
from . import views

app_name = 'User_Authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]