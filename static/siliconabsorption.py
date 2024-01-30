# Example script for the Silicon Absorption Calculator web app.

import numpy as np
import matplotlib.pyplot as plt

from solcore import material, si
from solcore.structure import Layer
from solcore.light_source import LightSource
from rayflare.ray_tracing import rt_structure
from rayflare.transfer_matrix_method import tmm_structure
from rayflare.textures import regular_pyramids
from rayflare.options import default_options


# Set up the parameters for the calculation
# These values are set by the webform
Si_width = 180e-6
ARC_width = 80e-9
shading = 0.02
texture = False
alrear = False

#Internal parameters not accessible from the webform
n_rays = 1000
profile_spacing = 1e-7

# Define the wavelength range of interest
wavelengths = si(np.linspace(280, 1180, 50), 'nm')

# load the AM1.5G spectrum to calculate maximum possible short-circuit currents
AM15G = LightSource(source_type='standard', version='AM1.5g', x=wavelengths,
                    output_units='photon_flux_per_m')

#Import relevant materials
Si = material("Si")()
SiN = material("Si3N4")()
Air = material("Air")()
Al = material("Al")()

#Define the simulation options
options = default_options()
options.pol = 'u'
options.wavelength = wavelengths
options.coherent = False
options.depth_spacing = profile_spacing

# Setup different structures depending on the form input.

if texture == False: # Is this a planar or textured calculation?
    if ARC_width == 0 :  # Planar Si, with no anti-reflection coating
        if alrear == False :
            structure = tmm_structure([Layer(width=Si_width, material=Si)], incidence=Air, transmission=Air)
            options.coherency_list = ['i']
        else:
            structure = tmm_structure([Layer(width=Si_width, material=Si)], incidence=Air, transmission=Al)
            options.coherency_list = ['i']
    else :  # Planar Si, with an Si3N4 anti-reflection coating of thickness ARC_width
        if alrear == False :    #
            structure=tmm_structure([Layer(width=ARC_width, material=SiN)] + [Layer(width=Si_width, material=Si)],
                  incidence=Air, transmission=Air)
            options.coherency_list = ['c', 'i']
        else:
            structure = tmm_structure(
                [Layer(width=ARC_width, material=SiN)] + [Layer(width=Si_width, material=Si)],
                incidence=Air, transmission=Al)
            options.coherency_list = ['c', 'i']

else :  # In the case of a textured surface setup some additional variables
    # Texture parameters
    front_texture = regular_pyramids(elevation_angle=55, upright=True)
    rear_texture = regular_pyramids(elevation_angle=55, upright=False)
    # Simulation options
    options.nx = 20
    options.ny = 20
    options.n_rays = n_rays
    options.bulk_profile = True
    options.depth_spacing_bulk = profile_spacing
    options.project_name = "Si_optics"

    if ARC_width==0: # In the case of no ARC.
        structure = rt_structure(textures=[front_texture, rear_texture],
                                 materials=[Si],
                                 widths=[Si_width],
                                 incidence=Air,
                                 transmission=Air,
                                 options=options)
    else:   # In the case of an ARC
        front_texture_ARC = regular_pyramids(elevation_angle=55, upright=True,
                                     interface_layers=[Layer(ARC_width, SiN)])
        options.coherency_list = ['c', 'i']
        if alrear == False: # In the case of no Al rear reflector
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

# Store wavelengths in the instance variable xpoints incase it needs to be saved later
xpointsR = wavelengths * 1e9

# Extract the absorption data depending on the method used:
if texture == False:
    ypointsA = calculation_result['A']
else:
    ypointsA = calculation_result['A_per_layer'][:, 0]

# Store reflectance data in an instance variable ypointsR incase it needs to be saved later
ypointsR = calculation_result['R']*(1-shading)+shading

# calculate cumulative generation

if texture == True:
    absorption_profile = calculation_result['profile'] * 1e6  # array with dimensions (n_wavelengths, n_depths)
# units are m^-1

else:
    exclude_points = np.ceil(ARC_width / profile_spacing)  # figure out how many points to exclude for the ARC
    planar_result_ARC = structure.calculate_profile(options)
    absorption_profile = planar_result_ARC['profile'][:,int(exclude_points):] * 1e6  # array with dimensions (n_wavelengths, n_depths)

# integrate over wavelengths with the photon flux:
weighted_absorption = absorption_profile * AM15G.spectrum(wavelengths)[1][:, None]
# units are m-1 * # of photons m^-2 m^-1, overall m^-4

# integrate over wavelengths
total_generation = np.trapz(weighted_absorption, wavelengths, axis=0)
# units are # of photons m^-3, as a function of depth in m

cumulative_generation = np.cumsum(total_generation) * profile_spacing
# units are # of photons m^-3, as a function of depth in m

depth = np.linspace(0, Si_width, len(cumulative_generation))
# I guess PC1D wants this in units of m^-2 cm-1, so divide by 10?
xpointsG=depth * 1e6
ypointsG=(1-shading)*cumulative_generation / 10

# Save data
np.savetxt("RayFlare_cumulative_generation.txt",np.column_stack((xpointsG,ypointsG)))
np.savetxt("RayFlare_cumulative_reflectance.txt",np.column_stack((xpointsR,ypointsR)))


# Plot the graph

plt.plot(xpointsR,ypointsA*(1-shading), label='A')
plt.plot(xpointsR,ypointsR, label='R')
plt.text(250,0.95, 'Mean R='+str("%.3f" % np.mean(ypointsR)))
weighted_photon_flux = AM15G.spectrum(wavelengths)[1] / np.max(AM15G.spectrum(wavelengths)[1])
plt.text(250,1.005, 'AM1.5G weighted mean R='+str("%.3f" % np.mean(ypointsR*weighted_photon_flux)))
plt.xlabel('Wavelength (nm)')
plt.ylabel('Absorption & Reflection')
plt.ylim(0, 1.05)
plt.legend()
plt.grid()
plt.show()




