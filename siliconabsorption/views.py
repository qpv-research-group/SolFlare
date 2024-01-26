import geocoder
import requests
from datetime import datetime
from django.http import HttpResponse

def temp_here(request):
    location = geocoder.ip('me').latlng
    endpoint = "https://api.open-meteo.com/v1/forecast"
    api_request = f"{endpoint}?latitude={location[0]}&longitude={location[1]}&hourly=temperature_2m"
    now = datetime.now()
    hour = now.hour
    meteo_data = requests.get(api_request).json()
    temp = meteo_data['hourly']['temperature_2m'][hour]
    return HttpResponse(f"Ned's amazing local thermometer - it is {temp} degrees Celsius outside")