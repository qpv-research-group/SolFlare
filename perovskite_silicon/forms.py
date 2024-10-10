from django import forms

class layerParameters(forms.Form):
    pero_thickness = forms.FloatField(label='Perovskite thickness (µm)', initial=0.5)
    silicon_thickness = forms.FloatField(label='Si thickness (µm)', initial=180)
    arc_thickness = forms.FloatField(label='ARC thickness (nm)', initial=80)
    # texture = forms.BooleanField(label='Texture?', initial=False,required=False)
    agrear = forms.BooleanField(label='Rear Ag mirror?', initial=False,required=False)

class textureParameters(forms.Form):
    front_texture = forms.BooleanField(label='Front texture?', initial=False, required=False)
    middle_texture = forms.BooleanField(label='Pero/Si interface texture?', initial=False, required=False)
    rear_texture = forms.BooleanField(label='Rear texture?', initial=False, required=False)
