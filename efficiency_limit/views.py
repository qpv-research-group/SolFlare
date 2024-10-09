import numpy as np
from django.shortcuts import render
from solcore.light_source import LightSource
from solcore.solar_cell import SolarCell
from solcore.solar_cell_solver import solar_cell_solver
from solcore.structure import Junction


def calculate_efficiency(request):
    # Generate solar spectrum data
    wl = np.linspace(280, 4400, 200) * 1e-9  # Reduced number of points for performance
    light = LightSource(source_type='standard', version='AM1.5g', x=1240 / (wl * 1e9),
                        output_units='photon_flux_per_ev')

    # Convert wavelength to energy in eV
    energy_ev = 1240 / (wl * 1e9)
    energy_ev = energy_ev[::-1]

    spectrum = light.spectrum(energy_ev)[1]

    spectrum_data = [{'x': float(e), 'y': float(i)} for e, i in zip(energy_ev, spectrum)]

    context = {
        'spectrum_data': spectrum_data,
    }

    if request.method == 'POST':
        eg_value = float(request.POST.get('eg_value', 1.0))

        # Your efficiency calculation code here
        back_reflector = True
        T = 298
        V = np.arange(0, 4, 0.01)
        ideality = 1 / np.sqrt(2) if back_reflector else 1

        junction_list = [Junction(kind='DB', T=T, Eg=eg_value, A=1, R_shunt=np.inf, n=ideality)]
        my_solar_cell = SolarCell(junction_list, T=T, R_series=0)

        solar_cell_solver(my_solar_cell, 'iv',
                          user_options={'T_ambient': T, 'db_mode': 'top_hat', 'voltages': V,
                                        'light_iv': True,
                                        'internal_voltages': np.arange(-1, np.sum([eg_value]) + 0.8,
                                                                       0.01),
                                        'wavelength': wl,
                                        'mpp': True, 'light_source': light})

        # Get efficiency values
        efficiency = my_solar_cell.iv.Eta * 100
        voc = my_solar_cell.iv.Voc
        jsc = my_solar_cell.iv.Isc
        ff = my_solar_cell.iv.FF * 100

        context.update({
            'efficiency': efficiency,
            'voc': voc,
            'jsc': jsc,
            'ff': ff,
            'eg_value': eg_value,
        })

    return render(request, 'calculate.html', context)