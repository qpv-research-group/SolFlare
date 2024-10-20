from solcore.solar_cell import SolarCell
from solcore.solar_cell_solver import solar_cell_solver
from solcore.structure import Junction
from solcore.state import State
import numpy as np

class cellCalculator():

    def __init__(self, wl, light):
        self.wl = wl
        self.light = light

    def get_data(self, request):

        # num_junctions = int(request.POST.get('num_junctions', 1))
        num_junctions = 2
        ext_bias = float(request.POST.get('external_voltage', 0))
        print('here')
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
            'internal_voltages': np.arange(-2, np.sum(eg_values) + 0.8, 0.01),
            'wavelength': self.wl,
            'mpp': True,
            'light_source': self.light,
                         })

        solar_cell_solver(my_solar_cell, 'iv',
                          user_options=options)

        # IV curve will have -ve currents and -ve voltages. Want +ve/+ve for plotting
        top_current = -my_solar_cell(0).iv(options.internal_voltages)/10 # Convert to mA/cm^2
        bottom_current = -my_solar_cell(1).iv(options.internal_voltages)/10 # Convert to mA/cm^2

        overall_I = my_solar_cell.iv.IV[1]/10
        overall_V = my_solar_cell.iv.IV[0]
        # this already has the right sign.

        # find current at external voltage:
        ext_bias_index = np.argmin(np.abs(overall_V - ext_bias))
        ext_bias_current = overall_I[ext_bias_index]

        # find the bias of the individual junctions at which this current occurs:
        top_ind = np.argmin(np.abs(top_current - ext_bias_current))
        bottom_ind = np.argmin(np.abs(bottom_current - ext_bias_current))

        top_junction_bias = options.internal_voltages[top_ind]
        bottom_junction_bias = options.internal_voltages[bottom_ind]

        # figure out which junction is 'pinning' the voltage, i.e. has a high slope close to the
        # current we are setting it at:

        slope_top = np.abs(top_current[top_ind + 1] - top_current[top_ind]) / 0.02
        slope_bottom = np.abs(bottom_current[bottom_ind + 1] - bottom_current[bottom_ind]) / 0.02

        if slope_top > slope_bottom:
            bottom_junction_bias = ext_bias - top_junction_bias

        else:
            top_junction_bias = ext_bias - bottom_junction_bias

        # Get efficiency values
        efficiency = np.round(my_solar_cell.iv.Eta * 100, 2)
        voc = np.round(my_solar_cell.iv.Voc, 3)
        jsc = np.round(my_solar_cell.iv.Isc/10, 1)
        ff = np.round(my_solar_cell.iv.FF * 100, 2)

        jsc_per_junction = [-my_solar_cell[i1].iv(0)/10 for i1 in range(len(eg_values))]

        return {
                'efficiency': efficiency,
                'voc': voc,
                'jsc': jsc,
                'ff': ff,
                'jsc_per_junction': jsc_per_junction,
                'internal_bias': options.internal_voltages.tolist(),
                'top_current': top_current.tolist(),
                'bottom_current': bottom_current.tolist(),
                'overall_I': overall_I.tolist(),
                'overall_V': overall_V.tolist(),
                'highest_I': np.max([np.max(top_current), np.max(bottom_current)]),
                'ext_bias_current': ext_bias_current,
                'ext_bias_actual': overall_V[ext_bias_index],
                'top_junction_voltage': top_junction_bias,
                'bottom_junction_voltage': bottom_junction_bias
            }
