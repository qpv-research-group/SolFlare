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

def generate_svg(front_text, layers, agrear):
    base_colors = sns.cubehelix_palette(len(layers) - 2, start=2.2, rot=0.04, dark=0.2, light=0.8)
    colors = ["rgba(255, 255, 255, 1.0)"] + [f"rgba({int(r * 255)},{int(g * 255)},{int(b * 255)}, 1.0)" for r, g, b in base_colors]

    if agrear:
        colors.append("rgba(100, 100, 100, 1.0)")

    else:
        colors.append("rgba(255, 255, 255, 1.0)")


    texture_list = [layer.get('textured') for layer in layers]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">'
    y = 200
    for i in range(len(layers) - 1, -1, -1):  # Reverse order to draw from bottom to top
        layer = layers[i]
        height = layer['height']
        color = colors[i]
        if texture_list[i]:
            # Draw the layer above first
            if i > 0:
                svg += f'<rect x="0" y="{y - height}" width="300" height="{height}" fill="{colors[i - 1]}" />'
            # Then draw the zigzag pattern
            svg += f'<path d="M0 {y} L300 {y} L300 {y - height} '
            for x in range(300, -1, -30):
                svg += f'L{x} {y - height + 20 if x % 60 == 0 else y - height} '
            svg += f'L0 {y - height} Z" fill="{color}" />'
        else:
            svg += f'<rect x="0" y="{y - height}" width="300" height="{height}" fill="{color}" />'
        y -= height
    svg += '</svg>'
    return svg


from django.shortcuts import render
import json

# ... (other imports remain the same)

def solar_cell_view(request):
    global graphobj

    layer_form = layerParameters(request.POST or None)
    texture_form = textureParameters(request.POST or None)

    if request.method == 'POST' and 'calculate' in request.POST:
        if layer_form.is_valid() and texture_form.is_valid():
            # Process form data
            pero_thickness = layer_form.cleaned_data['pero_thickness']
            silicon_thickness = layer_form.cleaned_data['silicon_thickness']
            arc_thickness = layer_form.cleaned_data['arc_thickness']
            agrear = layer_form.cleaned_data['agrear']

            front_text = texture_form.cleaned_data['front_texture']
            middle_text = texture_form.cleaned_data['middle_texture']
            rear_text = texture_form.cleaned_data['rear_texture']

            graphobj.setvalues(silicon_thickness * 1e-6, pero_thickness * 1e-9, arc_thickness * 1e-9,
                               agrear, front_text, middle_text, rear_text)
            graph_data = graphobj.getgraph()
        else:
            graph_data = None
    else:
        layer_form = layerParameters()
        texture_form = textureParameters()
        front_text = False
        middle_text = False
        rear_text = False
        graph_data = None
        agrear = False

    layers = [
        {"height": 10, "textured": False},
        {"height": 35, "textured": front_text},
        {"height": 115, "textured": middle_text},
        {"height": 30, "textured": rear_text},
    ]

    svg_content = generate_svg(front_text, layers, agrear)

    context = {
        'form': layer_form,
        'form_texture': texture_form,
        'svg_content': mark_safe(svg_content),
    }

    if graph_data:
        context['graph_data'] = mark_safe(json.dumps(graph_data))

    return render(request, 'perovskite_silicon.html', context)
