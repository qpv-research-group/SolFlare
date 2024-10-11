from django.urls import path
from . import views

urlpatterns = [
    path('', views.inputparams, name='input_params'),
]