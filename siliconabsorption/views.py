import geocoder
import requests
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from .forms import inputParameters




def inputparams(request):

    if request.method == 'POST':
        form = inputParameters(request.POST)
        if form.is_valid():
            arc_thickness = form.cleaned_data['arc_thickness']
            texture_height = form.cleaned_data['texture_height']
            print(arc_thickness, texture_height)
            return render(request, 'index.html', {'form':form,'value':arc_thickness*texture_height})

    form=inputParameters()
    return render(request, 'index.html', {'form':form,'value':0})


 #   if request.method == 'POST':
 #       data_sent=request.POST['datasent']
 #       return render(request,'index.html',{'multiply': data_sent})

#    return render(request,'index.html')
