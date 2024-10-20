import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from solcore.light_source import LightSource

from .models import cellCalculator

#@csrf_exempt
def junction_bias(request):
    # Generate solar spectrum data
    wl = np.linspace(280, 4400, 200) * 1e-9
    light = LightSource(source_type='standard', version='AM1.5g', x=1240 / (wl * 1e9),
                        output_units='photon_flux_per_ev')

    energy_ev = 1240 / (wl * 1e9)
    energy_ev = energy_ev[::-1]

    spectrum = light.spectrum(energy_ev)[1]

    spectrum_data = [{'x': float(e), 'y': float(i)} for e, i in zip(energy_ev, spectrum)]

    graphobj = cellCalculator(wl, light)

    print(request.method)

    if request.method == 'POST':
        result_dict = graphobj.get_data(request)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(result_dict)

    return render(request, 'junction_bias.html', {'spectrum_data': spectrum_data})