from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculate_lcoe, name='calculate_lcoe'),
]