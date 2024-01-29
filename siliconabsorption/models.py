import base64,urllib
import io

from django.db import models

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


class siliconCalculator:
# Constructor that sets up empty instance varibles
    def __init__(self):
        self.ARC_width = 80e-9
        self.shading = 2
        self.texture = False
        self.alrear = False
        self.xpointsR = np.empty(0)
        self.ypointsR = np.empty(0)
        self.xpointsG = np.empty(0)
        self.ypointsG = np.empty(0)

# A method that sets parameters according to the form input
    def setvalues(self,shading,arcthickness,texture,alrear):
        self.shading = shading/100      # Shading is passed as a fraction from views.py
        self.ARC_width = arcthickness   # ARC thickness is passed in units of [m] from views.py
        self.texture = texture
        self.alrear = alrear

    def getgraph(self):
        Si_width = 190e-6
        n_rays = 2000

        wavelengths = si(np.linspace(280, 1180, 50), 'nm')

        # load the AM1.5G spectrum to calculate maximum possible short-circuit currents
        AM15G = LightSource(source_type='standard', version='AM1.5g', x=wavelengths,
                            output_units='photon_flux_per_m')

        Si = material("Si")()
        SiN = material("Si3N4")()
        Air = material("Air")()
        Al = material("Al")()

        options = default_options()
        options.pol = 'u'
        options.wavelength = wavelengths
        options.coherent = False

# Setup different structures depending on the form input.

        if self.texture == False: # Is this a planar or textured calculation?
            if self.ARC_width == 0 :  # Planar Si, with no anti-reflection coating
                if self.alrear == False :
                    structure = tmm_structure([Layer(width=Si_width, material=Si)], incidence=Air, transmission=Air)
                    options.coherency_list = ['i']
                else:
                    structure = tmm_structure([Layer(width=Si_width, material=Si)], incidence=Air, transmission=Al)
                    options.coherency_list = ['i']
            else :  # Planar Si, with an Si3N4 anti-reflection coating of thickness ARC_width
                if self.alrear == False :    #
                    structure=tmm_structure([Layer(width=self.ARC_width, material=SiN)] + [Layer(width=Si_width, material=Si)],
                          incidence=Air, transmission=Air)
                    options.coherency_list = ['c', 'i']
                else:
                    structure = tmm_structure(
                        [Layer(width=self.ARC_width, material=SiN)] + [Layer(width=Si_width, material=Si)],
                        incidence=Air, transmission=Al)
                    options.coherency_list = ['c', 'i']



        else :  # In the case of a textured surface setup some additional variables
            # Texture parameters
            front_texture = regular_pyramids(elevation_angle=55, upright=True)
            rear_texture = regular_pyramids(elevation_angle=55, upright=False)
            # Simulation options
#            options.coherency_list = ['c', 'i'] # Trying to solve an error translating Phoebe's code to this model.  In P's code this option gets defined earlier.
            options.nx = 20
            options.ny = 20
            options.n_rays = n_rays
            options.bulk_profile = True
            options.depth_spacing_bulk = 1e-7  # every 100 nm
            options.project_name = "Si_optics"

            if self.ARC_width==0: # In the case of no ARC.
                structure = rt_structure(textures=[front_texture, rear_texture],
                                         materials=[Si],
                                         widths=[Si_width],
                                         incidence=Air,
                                         transmission=Air,
                                         options=options)
            else:   # In the case of an ARC
                front_texture_ARC = regular_pyramids(elevation_angle=55, upright=True,
                                             interface_layers=[Layer(self.ARC_width, SiN)])
                options.coherency_list = ['c', 'i']
                if self.alrear == False: # In the case of no Al rear reflector
                    structure = rt_structure(textures=[front_texture_ARC, rear_texture],
                                             materials=[Si],
                                             widths=[Si_width],
                                             incidence=Air,
                                             transmission=Air,
                                             use_TMM=True,
                                             options=options,
                                             save_location='current')
                else:
                    structure = rt_structure(textures=[front_texture_ARC, rear_texture],
                                    materials=[Si],
                                    widths=[Si_width],
                                    incidence=Air,
                                    transmission=Al,
                                    use_TMM=True,
                                    options=options,
                                    save_location='current')


# Perform the calculation
        calculation_result=structure.calculate(options)

        #The ypoints depend upon whether the structure is planar or textured.
        if self.texture == False:
            self.ypointsR = calculation_result['A']
        else:
            self.ypointsR = calculation_result['A_per_layer'][:, 0]

        # define xpoints as wavelength.
        self.xpointsR = wavelengths * 1e9


        # Plot the graph

        plt.clf() # Clear the figure so that graphs don't stack up.

        plt.plot(self.xpointsR, self.ypointsR, label=self.ARC_width)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Absorption in Si')
        plt.legend()
        plt.grid()

        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        # adapted from https://sukhbinder.wordpress.com/2022/04/13/rendering-matplotlib-graphs-in-django/
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri
    def downloadR(self, writer):
        # Save the generation file

        # Iterate through xpoints and ypoints and add to csv file
        for indx in range(self.xpointsR.shape[0]):
            writer.writerow([self.xpointsR[indx], self.ypointsR[indx]])
        return writer

    def downloadG(self, writer):
        # Save the generation file

        # Iterate through xpoints and ypoints and add to csv file
        for indx in range(self.xpointsR.shape[0]):
            writer.writerow([self.xpointsR[indx], self.ypointsR[indx]])
        return writer



