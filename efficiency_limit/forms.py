from django import forms


class EgForm(forms.Form):
    num_junctions = forms.IntegerField(
        label='Number of Junctions',
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'id': 'num_junctions'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically add fields for bandgaps
        num_junctions = self.data.get('num_junctions', 1)
        try:
            num_junctions = int(num_junctions)
        except ValueError:
            num_junctions = 1

        for i in range(1, num_junctions + 1):
            field_name = f'eg_value_{i}'
            self.fields[field_name] = forms.FloatField(
                label=f'Eg Value {i}',
                min_value=0,
                max_value=10,
                initial=1.0,
                widget=forms.NumberInput(attrs={'class': 'eg-slider', 'id': f'eg_value_{i}'})
            )