from django.shortcuts import render
import seaborn as sns
from django.utils.safestring import mark_safe
from django.http import JsonResponse

from numba import config
config.DISABLE_JIT = True

import numpy as np
from solcore.light_source import LightSource

from rayflare.textures import regular_pyramids
import matplotlib.pyplot as plt

from solcore import material
from solcore.structure import Layer
from rayflare.options import default_options
from rayflare.ray_tracing import rt_structure
from time import time

from .forms import layerParameters, textureParameters
from .models import siliconCalculator

graphobj = siliconCalculator()

def generate_svg(layers):
    base_colors = sns.cubehelix_palette(len(layers), start=2.2, rot=0.1, dark=0.2, light=0.8)
    colors = [f"rgba({int(r * 255)},{int(g * 255)},{int(b * 255)},0.7)" for r, g, b in base_colors]

    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">'
    y = 200
    for i in range(len(layers) - 1, -1, -1):  # Reverse order to draw from bottom to top
        layer = layers[i]
        height = layer['height']
        color = colors[i]
        if layer.get('textured'):
            # Draw the layer above first
            if i > 0:
                svg += f'<rect x="0" y="{y - height}" width="300" height="{height}" fill="{colors[i - 1]}" />'
            # Then draw the zigzag pattern
            svg += f'<path d="M0 {y} L300 {y} L300 {y - height} '
            for x in range(300, -1, -30):
                svg += f'L{x} {y - height + (height/3) if x % 60 == 0 else y - height} '
            svg += f'L0 {y - height} Z" fill="{color}" />'
        else:
            svg += f'<rect x="0" y="{y - height}" width="300" height="{height}" fill="{color}" />'
        y -= height
    svg += '</svg>'
    return svg


def solar_cell_view(request):
    global graphobj

    texture = False

    total_height = 200
    layers = [
        # {"height": 50},  # Base layer
        {"height": total_height/2, "textured": True},  # Textured layer
        {"height": total_height/4},  # Fourth layer
        {"height": total_height/4},  # Top layer
    ]

    svg_content = generate_svg(layers)  # Generate your SVG content

    if request.method == 'POST':
        form = layerParameters(request.POST)
        if form.is_valid():
            silicon_thickness = form.cleaned_data['silicon_thickness']
            arc_thickness = form.cleaned_data['arc_thickness']
            agrear = form.cleaned_data['agrear']
            shading = form.cleaned_data['shading']
            graphobj.setvalues(silicon_thickness * 1e-6, shading / 100, arc_thickness * 1e-9,
                               texture, agrear)

        form_texture = textureParameters(request.POST)

        if form_texture.is_valid():
            front_text = form_texture.cleaned_data['front_texture']
            middle_text = form_texture.cleaned_data['middle_texture']
            rear_text = form_texture.cleaned_data['rear_texture']

    else:
        form = layerParameters()  # Create a new form instance with default values
        form_texture = textureParameters()

    context = {
        'form': form,
        'form_texture': form_texture,
        'graph': graphobj.getgraph(),
        'svg_content': mark_safe(svg_content),  # Make sure to import mark_safe
    }

    return render(request, 'perovskite_silicon.html', context)


def cell_calculation(request):
    # Your calculation code here
    Si = material("Si")()
    Air = material("Air")()
    Ag = material("Ag")()
    MgF2 = material("MgF2")()

    Pvk = material("Perovskite_CsBr_1p6eV")()

    n_rays = 200

    d = 100e-6

    wavelengths = np.linspace(300, 950, 50) * 1e-9

    AM15G = LightSource(source_type='standard', version='AM1.5g', x=wavelengths,
                        output_units='photon_flux_per_m')

    options = default_options()

    options.wavelength = wavelengths
    options.project_name = 'pvk_Si_analytical_RT'
    options.nx = 20
    options.ny = 20
    options.theta_in = 0.1
    options.parallel = False  # for this example, with this choice of wavelengths, initializing the parallel
    # threads takes more time than it saves on executing the ray-tracing. For a more transparent structure
    # (at longer wavelengths in this case), this would no longer be true.
    options.randomize_surface = True
    options.I_thresh = 1e-3
    options.depth_spacing_bulk = 1e-8
    options.n_rays = n_rays
    options.maximum_passes = 100
    options.n_rays = n_rays
    options.pol = 'u'

    front_text = regular_pyramids(52, True, 1,
                                  interface_layers=[Layer(100e-9, MgF2), Layer(1000e-9, Pvk)],
                                  analytical=True)

    # note: not setting analytical = True for the last surface; rays will no longer be travelling in a
    # single direction after interacting with front_text_2, so this surface will not be treated analytically
    # anyway, even if we set analytical = True.

    rear_text = regular_pyramids(52, False, 1)

    rt_str = rt_structure(textures=[front_text, rear_text], materials=[Si],
                          widths=[d], incidence=Air, transmission=Ag,
                          options=options, use_TMM=True, save_location='current',
                          overwrite=True)


    return JsonResponse({'efficiency': 25.0})

