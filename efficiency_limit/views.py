import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .forms import EgForm
from solcore.light_source import LightSource
from solcore.solar_cell import SolarCell
from solcore.solar_cell_solver import solar_cell_solver
from solcore.structure import Junction


def calculate_efficiency(request):
    context = {'form': EgForm()}

    if request.method == 'POST':
        form = EgForm(request.POST)
        if form.is_valid():
            eg_value = form.cleaned_data['eg_value']

            # Your provided code here, modified to use eg_value
            back_reflector = True
            wl = np.linspace(300, 4000, 4000) * 1e-9
            light = LightSource(source_type='standard', version='AM1.5g',
                                x=1240 / (wl * 1e9), output_units='photon_flux_per_ev')
            T = 298
            V = np.arange(0, 4, 0.01)
            ideality = 1 / np.sqrt(2) if back_reflector else 1

            junction_list = [Junction(kind='DB', T=T, Eg=eg_value, A=1, R_shunt=np.inf, n=ideality)]
            my_solar_cell = SolarCell(junction_list, T=T, R_series=0)

            solar_cell_solver(my_solar_cell, 'iv',
                              user_options={'T_ambient': T, 'db_mode': 'top_hat', 'voltages': V,
                                            'light_iv': True,
                                            'internal_voltages': np.arange(-1,
                                                                           np.sum([eg_value]) + 0.8,
                                                                           0.01),
                                            'wavelength': wl,
                                            'mpp': True, 'light_source': light})

            # Generate plot
            plt.figure()
            plt.plot(1240 / (wl * 1e9), light.spectrum()[1])
            plt.xlabel('Energy (eV)')
            plt.ylabel('Spectral intensity')
            plt.title('Light Source Spectrum')

            # Save plot to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            # Encode the image to base64
            graphic = base64.b64encode(image_png).decode('utf-8')

            # Get efficiency values
            efficiency = my_solar_cell.iv.Eta * 100
            voc = my_solar_cell.iv.Voc
            jsc = my_solar_cell.iv.Isc
            ff = my_solar_cell.iv.FF * 100

            context.update({
                'form': form,
                'graphic': graphic,
                'efficiency': efficiency,
                'voc': voc,
                'jsc': jsc,
                'ff': ff,
            })

    return render(request, 'calculate.html', context)