from django.urls import path
from . import views
urlpatterns = [
    path('siliconabsorption/', views.temp_here, name='temp_here'),
]
