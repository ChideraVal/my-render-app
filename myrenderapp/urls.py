from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home),
    path('pay/', views.pay),
    path('verify/', views.activate_order)
]