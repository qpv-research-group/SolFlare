from django.urls import path
from . import views

urlpatterns = [
    path('', views.junction_bias, name='junction_bias'),
]