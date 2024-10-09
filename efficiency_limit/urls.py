from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculate_efficiency, name='calculate_efficiency'),
]