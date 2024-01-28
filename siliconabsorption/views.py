import csv
from django.http import HttpResponse
from django.shortcuts import render
from .forms import inputParameters
from .models import siliconCalculator


graphobj=siliconCalculator()
def inputparams(request):
    global graphobj

    if 'calculate' in request.POST:
        form = inputParameters(request.POST)
        if form.is_valid():
            arc_thickness = form.cleaned_data['arc_thickness']
            texture = form.cleaned_data['texture']
            alrear = form.cleaned_data['alrear']
            graphobj.setvalues(arc_thickness*1e-9, texture,alrear)
            return render(request, 'index.html', {'form':form,'graph':graphobj.getgraph()})

    if 'download' in request.POST:
        # code based on https://docs.djangoproject.com/en/5.0/howto/outputting-csv/
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="siliconR.txt"'},
        )
        writer = csv.writer(response,dialect='excel-tab')
        graphobj.getcsv(writer)
        return response

    form=inputParameters()
    return render(request, 'index.html', {'form':form,'graph':0})


