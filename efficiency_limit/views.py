import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from solcore.light_source import LightSource
from solcore.solar_cell import SolarCell
from solcore.solar_cell_solver import solar_cell_solver
from solcore.structure import Junction
from solcore.state import State

@csrf_exempt
def calculate_efficiency(request):
    # Generate solar spectrum data
    wl = np.linspace(280, 4400, 200) * 1e-9
    light = LightSource(source_type='standard', version='AM1.5g', x=1240 / (wl * 1e9),
                        output_units='photon_flux_per_ev')

    energy_ev = 1240 / (wl * 1e9)
    energy_ev = energy_ev[::-1]

    spectrum = light.spectrum(energy_ev)[1]

    spectrum_data = [{'x': float(e), 'y': float(i)} for e, i in zip(energy_ev, spectrum)]

    if request.method == 'POST':
        num_junctions = int(request.POST.get('num_junctions', 1))
        eg_values = [float(request.POST.get(f'eg_value_{i}', 1.0)) for i in range(1, num_junctions + 1)]

        # Your efficiency calculation code here
        back_reflector = True
        T = 298
        V = np.arange(0, np.sum(eg_values) + 0.2, 0.01)
        ideality = 1 / np.sqrt(2) if back_reflector else 1

        junction_list = []

        for eg in eg_values:
            junction_list.append(Junction(kind='DB', T=T, Eg=eg, A=1, R_shunt=np.inf, n=ideality))

        my_solar_cell = SolarCell(junction_list, T=T, R_series=0)

        options = State({
            'T_ambient': T,
            'db_mode': 'top_hat',
            'voltages': V,
            'light_iv': True,
            'internal_voltages': np.arange(-1, np.sum(eg_values) + 0.8, 0.01),
            'wavelength': wl,
            'mpp': True,
            'light_source': light,
                         })

        solar_cell_solver(my_solar_cell, 'iv',
                          user_options=options)

        # Get efficiency values
        efficiency = np.round(my_solar_cell.iv.Eta * 100, 2)
        voc = np.round(my_solar_cell.iv.Voc, 3)
        jsc = np.round(my_solar_cell.iv.Isc/10, 1)
        ff = np.round(my_solar_cell.iv.FF * 100, 2)

        jsc_per_junction = [-my_solar_cell[i1].iv(0)/10 for i1 in range(len(eg_values))]

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'efficiency': efficiency,
                'voc': voc,
                'jsc': jsc,
                'ff': ff,
                'jsc_per_junction': jsc_per_junction,
            })

    return render(request, 'calculate.html', {'spectrum_data': spectrum_data})