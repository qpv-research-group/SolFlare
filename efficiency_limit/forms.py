from django import forms

class EgForm(forms.Form):
    eg_value = forms.FloatField(label='Eg Value', min_value=0, max_value=10)
