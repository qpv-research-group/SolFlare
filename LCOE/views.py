import numpy as np
from django.shortcuts import render
from .forms import lcoeParameters
import json

#@csrf_exempt
def calculate_lcoe(request):
    # Generate solar spectrum data
    form = lcoeParameters(request.POST or None)

    print("Request method:", request.method)
    print("POST data:", request.POST)
    print("Form is valid:", form.is_valid() if request.method == 'POST' else "Not checked")

    results = {}

    if request.method == 'POST' and 'calculate' in request.POST:

        capacity_factor_min = form.cleaned_data['capacity_factor_min']
        capacity_factor_max = form.cleaned_data['capacity_factor_max']
        capacity_cost_min = form.cleaned_data['capacity_cost_min']
        capacity_cost_max = form.cleaned_data['capacity_cost_max']

        pVCapacity = 5000
        # capacityCost=1.4
        bosCost = 0.0
        oandmCost = form.cleaned_data['om_cost']
        # capitalInvestment=pVCapacity*(capacityCost + bosCost)

        # capacityFactor = 0.32
        performanceRatio = 1
        degradation = form.cleaned_data['pv_degradation'] / 100
        inflation = 0.0
        years = form.cleaned_data['lifetime']

        r = form.cleaned_data['discount_rate'] / 100

        capacityCost = np.linspace(capacity_cost_min, capacity_cost_max, 30)
        capacityFactor = np.linspace(capacity_factor_min / 100, capacity_factor_max / 100, 30)

        xx, yy = np.meshgrid(capacityCost, capacityFactor, sparse=True)

        def getLCOE(capitalInvestment, oandmCost, inflation, capacityFactor, pVCapacity,
                    performanceRatio, degradation, r, years):
            investment = [0 for x in range(years)]
            investment[0] = capitalInvestment
            oandm = [pVCapacity * oandmCost * (1 + inflation * x) / ((1 + r) ** (x)) for x in
                     range(years)]
            oandm[0] = 0

            electricity = [
                365 * 24 * pVCapacity * capacityFactor * performanceRatio * (1 - degradation * x) / (
                            1000 * (1 + r) ** (x + 1)) for x in range(years - 1)]
            electricity.insert(0, 0)

            npv = [(investment[x] + oandm[x]) for x in range(years)]
            totalnpv = sum(npv)
            totalelectricity = sum(electricity)
            return totalnpv / totalelectricity

        # print("Capacity cost: $",capacityCost,"Wp")
        # print("Operation & Maintenance cost: $",oandmCost," p.a.")
        # print("Inflation",inflation)
        # print("Capacity factor:",capacityFactor)
        # print("Performance ratio:", performanceRatio)
        # print("Degradation:",degradation)
        # print("Discount rate:",r)
        # print("LCOE: {0:.3f}".format(getLCOE(capitalInvestment,oandmCost,inflation,capacityFactor,pVCapacity,performanceRatio,degradation,r,years)))

        z = getLCOE(pVCapacity * (xx + bosCost), oandmCost, inflation, yy, pVCapacity, performanceRatio,
                    degradation, r, years) * 1000

        # Explicitly create 2D list
        z_2d = z.tolist() if isinstance(z, np.ndarray) else z

        results = {
            'z': z_2d,
            'capacityCost': capacityCost.tolist(),
            'capacityFactor': (capacityFactor*100).tolist(),
        }

    # Print out the shapes to verify
        print("Z shape:", np.array(z_2d).shape)
        print("Capacity Cost shape:", len(capacityCost))
        print("Capacity Factor shape:", len(capacityFactor))

    context = {
        'form': form,
        'results_json': json.dumps(results),
    }

    return render(request, 'lcoe.html', context)