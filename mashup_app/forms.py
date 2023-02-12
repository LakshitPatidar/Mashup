from django import forms
from .models import Mashup

class MashupForm(forms.ModelForm):
    class Meta:
        model = Mashup
        fields = ['singer_name', 'number_of_videos', 'duration', 'email']

    email = forms.EmailField(required=True)
