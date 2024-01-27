from django import forms

class inputParameters(forms.Form):
    arc_thickness = forms.FloatField(label='Arc Thickness (nm)', initial=100)
    texture_height = forms.FloatField(label='Texture Height (um)', initial=10)
