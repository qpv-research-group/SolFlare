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
        self.texture = False
        self.alrear = False
        self.xpoints = np.empty(0)
        self.ypoints = np.empty(0)

# A method that sets parameters according to the form input
    def setvalues(self,arcthickness,texture,alrear):
        self.ARC_width = arcthickness
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

        if self.ARC_width == 0 and self.texture == False:
            # Planar Si, with no anti-reflection coating
            structure = tmm_structure([Layer(width=Si_width, material=Si)], incidence=Air, transmission=Air)
            options.coherency_list = ['i']
        else:
            # Planar Si, with an Si3N4 anti-reflection coating of thickness ARC_width
            structure=tmm_structure([Layer(width=self.ARC_width, material=SiN)] + [Layer(width=Si_width, material=Si)],
                          incidence=Air, transmission=Air)
            options.coherency_list = ['c', 'i']

# Perform the calculation
        calculation_result=structure.calculate(options)

        #Store the data so that it persists for download...
        # Likely needs updating if what is downloaded is different to what is plotted...
        self.xpoints = wavelengths * 1e9
        self.ypoints = calculation_result['A']

        # Plot the graph

        plt.clf() # Clear the figure so that graphs don't stack up.

        plt.plot(wavelengths * 1e9, calculation_result['A'], label=self.ARC_width)
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

# Example of a class that can be used to generate a graph and download link
class plotter:
    def __init__(self):
        self.arcthickness = 0
        self.pyramidheight = 0
        self.xpoints = np.empty(0)
        self.ypoints = np.empty(0)

    def setvalues(self,arcthickness,pyramidheight):
        self.arcthickness = arcthickness
        self.pyramidheight = pyramidheight

    def getgraph(self):
        self.xpoints = np.arange(0, 10, 0.1)
        self.ypoints = self.pyramidheight*np.sin(self.xpoints*self.arcthickness)
        plt.clf()
        plt.plot(self.xpoints, self.ypoints)
        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        # adapted from https://sukhbinder.wordpress.com/2022/04/13/rendering-matplotlib-graphs-in-django/
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri

    def getcsv(self,writer):
        # Iterate through xpoints and ypoints and add to csv file
        writer.writerow(["xpoints", "ypoints"])
        for indx in range(self.xpoints.shape[0]):
            writer.writerow([self.xpoints[indx], self.ypoints[indx]])
        return writer

