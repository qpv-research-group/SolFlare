import base64,urllib
import io

from django.db import models

from numba import config
config.DISABLE_JIT = True

import numpy as np
import matplotlib.pyplot as plt

from solcore import material, si
from solcore.structure import Layer
from solcore.light_source import LightSource
from solcore.constants import q

from rayflare.ray_tracing import rt_structure
from rayflare.transfer_matrix_method import tmm_structure

from rayflare.textures import regular_pyramids
from rayflare.options import default_options

from time import time

class siliconCalculator:
# Constructor that sets up empty instance varibles
    def __init__(self):
        self.Si_width = 180e-6
        self.ARC_width = 80e-9
        self.agrear = False
        self.front_text = False
        self.middle_text = False
        self.back_text = False
        self.xpointsR = np.empty(0)
        self.ypointsA = np.empty(0)
        self.xpointsG = np.empty(0)
        self.ypointsG = np.empty(0)

# A method that sets parameters according to the form input
    def setvalues(self, Si_width, pero_width, arcthickness, agrear, front_text, middle_text, back_text):
        self.Si_width = Si_width      # Si thickness is passed in units of [m] from views.py
        self.pero_width = pero_width  # Perovskite thickness is passed in units of [m] from views.py
        self.ARC_width = arcthickness   # ARC thickness is passed in units of [m] from views.py
        self.agrear = agrear
        self.front_text = front_text
        self.middle_text = middle_text
        self.back_text = back_text
    def getgraph(self):

        n_rays = 100
        profile_spacing = 1e-7

        wavelengths = si(np.linspace(280, 1180, 50), 'nm')

        # load the AM1.5G spectrum to calculate maximum possible short-circuit currents
        AM15G = LightSource(source_type='standard', version='AM1.5g', x=wavelengths,
                            output_units='photon_flux_per_m')

        Si = material("Si")()
        Air = material("Air")()
        Ag = material("Ag")()
        pero = material("Perovskite_CsBr_1p6eV")()
        MgF2 = material("MgF2_RdeM")()

        options = default_options()
        options.pol = 'u'
        options.wavelength = wavelengths
        options.coherent = False
        options.depth_spacing = profile_spacing
        options.parallel = False

        if self.agrear:
            transmission = Ag

        else:
            transmission = Air

        # Setup different structures depending on the form input.
        if not np.any([self.front_text, self.middle_text, self.back_text]):
            calc_type = 'TMM'

        # elif not self.front_text and not self.middle_text and self.back_text:
        #     calc_type = 'combined'

        else:
            calc_type = 'RT'

        print(calc_type)

        if calc_type == 'TMM': # Is this a planar or textured calculation?
                structure = tmm_structure(
                    [
                        Layer(width=self.ARC_width, material=MgF2),
                        Layer(width=self.pero_width, material=pero),
                        Layer(width=self.Si_width, material=Si),

                    ],
                    incidence=Air, transmission=transmission)
                options.coherent = False
                options.coherency_list = ['c', 'c', 'i']

        elif calc_type == 'RT' :

            front_texture_ARC = regular_pyramids(elevation_angle=54, upright=True,
                                                 interface_layers=[
                                                     Layer(self.ARC_width, MgF2),
                                                    Layer(self.pero_width, pero)
                                                 ],
                                                 analytical=True)
            rear_texture = regular_pyramids(elevation_angle=54, upright=False)
            # Simulation options
            options.nx = 10
            options.ny = 10
            options.n_rays = n_rays
            options.bulk_profile = True
            options.depth_spacing_bulk = 50e-6
            options.project_name = "Si_optics"
            options.coherency_list = ['c', 'i']
            options.maximum_passes = 20

            structure = rt_structure(textures=[front_texture_ARC, rear_texture],
                            materials=[Si],
                            widths=[self.Si_width],
                            incidence=Air,
                            transmission=transmission,
                            use_TMM=True,
                            options=options,
                            save_location='current',
                            overwrite=True
                                     )


# Perform the calculation
        start = time()
        calculation_result = structure.calculate(options)
        print("calculation time:", time() - start)

        # Store wavelengths in the instance variable xpoints incase it needs to be saved later
        self.xpointsR = wavelengths * 1e9

        # Extract the absorption data depending on the method used:
        if calc_type == 'TMM':
            self.ypointsA_pero = calculation_result['A_per_layer'][:,1]
            self.ypointsA_Si = calculation_result['A_per_layer'][:,2]
        else:
            self.ypointsA_pero = calculation_result['A_per_interface'][0][:,1]
            self.ypointsA_Si = calculation_result['A_per_layer'][:,0]

        # Store reflectance data in an instance variable ypointsR incase it needs to be saved later
        self.ypointsR = calculation_result['R']

        # calculate cumulative generation
        # Plot the graph
        plt.clf() # Clear the figure so that graphs don't stack up.
        plt.plot(self.xpointsR, self.ypointsA_pero, label='Perovskite', color='r')
        plt.plot(self.xpointsR, self.ypointsA_Si, label='Si', color='k')
        plt.plot(self.xpointsR,self.ypointsR, label='R', color='b', linestyle='--')
        plt.text(250,0.95, 'Mean R='+str("%.3f" % np.mean(self.ypointsR)))
        weighted_photon_flux = AM15G.spectrum(wavelengths)[1] / np.max(AM15G.spectrum(wavelengths)[1])
        plt.text(250,1.005, 'AM1.5G weighted mean R='+str("%.3f" % np.mean(self.ypointsR*weighted_photon_flux)))
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Absorption & Reflection')
        plt.ylim(0, 1.05)
        plt.legend()
        plt.grid()

        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        # adapted from https://sukhbinder.wordpress.com/2022/04/13/rendering-matplotlib-graphs-in-django/
        buf = io.BytesIO()
        fig.savefig(buf, format='png',dpi=300)
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri

    def downloadR(self, writer):
        # Save the Reflectance file
        # Iterate through xpoints and ypoints and add to csv file
        for indx in range(self.xpointsR.shape[0]):
            writer.writerow([self.xpointsR[indx], self.ypointsR[indx]])
        return writer

    def downloadG(self, writer):
        # Save the generation file
        # Iterate through xpoints and ypoints and add to txt file
        for indx in range(self.xpointsG.shape[0]):
            writer.writerow([self.xpointsG[indx], self.ypointsG[indx]])
        return writer



