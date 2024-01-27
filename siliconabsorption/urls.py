from django.urls import path
from . import views
urlpatterns = [
    path('siliconabsorption/', views.inputparams, name='input_params'),
]
