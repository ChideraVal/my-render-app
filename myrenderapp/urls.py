from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home),
    path('login/', views.user_login),
    path('signup/', views.user_signup),
    path('edit/', views.user_edit),
    path('verify/<str:txref>/', views.activate_order)
]