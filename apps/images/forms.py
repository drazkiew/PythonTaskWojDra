from django import forms
from django.core.validators import MinValueValidator


class UploadImageForm(forms.Form):
    title = forms.CharField(
        required=False, max_length=80, initial=""
    )
    width = forms.IntegerField(
        required=False, initial=0, validators=[MinValueValidator(0)]
    )
    height = forms.IntegerField(
        required=False, initial=0, validators=[MinValueValidator(0)]
    )
    image = forms.ImageField()
