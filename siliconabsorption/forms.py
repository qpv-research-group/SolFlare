from django import forms

class inputParameters(forms.Form):
    arc_thickness = forms.FloatField(label='Frequency (au)', initial=10)
    texture_height = forms.FloatField(label='Amplitude (um)', initial=10)
