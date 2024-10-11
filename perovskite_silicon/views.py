import seaborn as sns
import numpy as np
from django.utils.safestring import mark_safe
from django.core.cache import cache

from numba import config
config.DISABLE_JIT = True

from .forms import layerParameters, textureParameters
from .models import siliconCalculator

graphobj = siliconCalculator()

def generate_svg(layers, agrear):
    # base_colors = sns.cubehelix_palette(len(layers) - 2, start=2.3, rot=0.02, dark=0.2, light=0.8)
    base_colors = np.array([[255,179,194], [160,208,246], [171,223,223], [229,211,162]])
    base_colors = base_colors[:(len(layers)-2)]
    colors = ["rgba(255, 255, 255, 1.0)"] + [f"rgba({int(r)},{int(g)},{int(b)}, 1.0)" for r, g, b in base_colors]

    if agrear:
        colors.append("rgba(180, 180, 180, 1.0)")

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

def solar_cell_view(request):
    global graphobj

    layer_form = layerParameters(request.POST or None)
    texture_form = textureParameters(request.POST or None)

    # Retrieve previous results from cache
    results = cache.get('calculation_results', [])

    graph_data = None
    front_text = False
    middle_text = False
    rear_text = False
    agrear = False

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

            # Add new result
            new_result = {
                'J_pero': graph_data['J_pero'],
                'J_Si': graph_data['J_Si'],
                'J_R': graph_data['J_R'],
                'J_T': graph_data['J_T'],
            }

            # Insert new result at the beginning
            results.insert(0, new_result)

            # Keep only the last 5 results
            results = results[:5]

            # Update cache with new results
            cache.set('calculation_results', results)

    layers = [
        {"height": 10, "textured": False},
        {"height": 35, "textured": front_text},
        {"height": 115, "textured": middle_text},
        {"height": 30, "textured": rear_text},
    ]

    svg_content = generate_svg(layers, agrear)

    context = {
        'form': layer_form,
        'form_texture': texture_form,
        'svg_content': mark_safe(svg_content),
        'results': results,
    }

    if graph_data:
        context['graph_data'] = mark_safe(json.dumps(graph_data))

    return render(request, 'perovskite_silicon.html', context)