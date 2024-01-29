import csv
from django.http import HttpResponse
from django.shortcuts import render
from .forms import inputParameters
from .models import siliconCalculator


graphobj=siliconCalculator()
def inputparams(request):
    global graphobj

    if 'calculate' in request.POST: # Actions to perform when [Calculate] is pressed
        form = inputParameters(request.POST)
        if form.is_valid():
            arc_thickness = form.cleaned_data['arc_thickness']
            texture = form.cleaned_data['texture']
            alrear = form.cleaned_data['alrear']
            shading = form.cleaned_data['shading']
            graphobj.setvalues(shading/100,arc_thickness*1e-9, texture,alrear)
            return render(request, 'index.html', {'form':form,'graph':graphobj.getgraph()})

    if 'downloadR' in request.POST: # Actions to perform when [Download Reflectance] is pressed
        # code based on https://docs.djangoproject.com/en/5.0/howto/outputting-csv/
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="silicon_R.txt"'},
        )
        writer = csv.writer(response,dialect='excel-tab')
        graphobj.downloadR(writer)
        return response

    if 'downloadG' in request.POST: # Actions to perform when [Download Generation] is pressed
        # code based on https://docs.djangoproject.com/en/5.0/howto/outputting-csv/
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="silicon_G.txt"'},
        )
        writer = csv.writer(response,dialect='excel-tab')
        graphobj.downloadG(writer)
        return response


    form=inputParameters()
    return render(request, 'index.html', {'form':form,'graph':0})


