from django.urls import path
from . import views

urlpatterns = [
    path('', views.solar_cell_view, name='solar_cell'),
]