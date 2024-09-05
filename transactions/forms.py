# forms.py

from django import forms
from .models import NameVariation  # Make sure this path is correct

class UploadFileForm(forms.Form):
    ofac_file = forms.FileField(required=False)
    un_file = forms.FileField(required=False)
    eu_file = forms.FileField(required=False)


from django import forms
from .models import NameVariation

class NameVariationForm(forms.ModelForm):
    class Meta:
        model = NameVariation
        fields = ['is_active']

class DisableNameVariationForm(forms.ModelForm):
    class Meta:
        model = NameVariation
        fields = ['is_active']
        widgets = {
            'is_active': forms.HiddenInput()
        }


# forms.py
from django import forms
from .models import NameVariation

class NameVariationForm(forms.ModelForm):
    

    class Meta:
        model = NameVariation
        fields = ['is_active']  # Include other fields as needed


        widgets = {
            'is_active': forms.Select(choices=[(True, 'Enabled'), (False, 'Disabled')])
        }



from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
