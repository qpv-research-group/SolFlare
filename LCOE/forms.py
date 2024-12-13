from django import forms

class lcoeParameters(forms.Form):
    lifetime = forms.IntegerField(label='Lifetime (years)', initial=30)
    discount_rate = forms.FloatField(label='Discount rate (%)', initial=7)
    om_cost = forms.FloatField(label='Operation & maintenance cost ($/Wp/year)', initial=0.013)
    # texture = forms.BooleanField(label='Texture?', initial=False,required=False)
    pv_degradation = forms.FloatField(label='PV degradation rate (%/year)', initial=0.5)

    # New fields for capacity factor range
    capacity_factor_min = forms.FloatField(
        label='Minimum Capacity Factor (%)',
        initial=15,
        min_value=0,
        max_value=100
    )
    capacity_factor_max = forms.FloatField(
        label='Maximum Capacity Factor (%)',
        initial=35,
        min_value=0,
        max_value=100
    )

    # New fields for capacity cost range
    capacity_cost_min = forms.FloatField(
        label='Minimum Capacity Cost ($/Wp)',
        initial=0.3,
        min_value=0
    )
    capacity_cost_max = forms.FloatField(
        label='Maximum Capacity Cost ($/Wp)',
        initial=0.75,
        min_value=0
    )

    def clean(self):
        cleaned_data = super().clean()

        # Validate capacity factor range
        cf_min = cleaned_data.get('capacity_factor_min')
        cf_max = cleaned_data.get('capacity_factor_max')
        if cf_min and cf_max and cf_min >= cf_max:
            raise forms.ValidationError(
                "Minimum capacity factor must be less than maximum capacity factor")

        # Validate capacity cost range
        cc_min = cleaned_data.get('capacity_cost_min')
        cc_max = cleaned_data.get('capacity_cost_max')
        if cc_min and cc_max and cc_min >= cc_max:
            raise forms.ValidationError(
                "Minimum capacity cost must be less than maximum capacity cost")

        return cleaned_data