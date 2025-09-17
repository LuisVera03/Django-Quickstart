from django import forms
from . import models

class Table3Form(forms.ModelForm):
    class Meta:
        model = models.Table3
        fields = '__all__'

class Table2Form(forms.ModelForm):
    class Meta:
        model = models.Table2
        fields = '__all__'

class Table1Form(forms.ModelForm):
    class Meta:
        model = models.Table1
        fields = '__all__'
        widgets = {
            # Customize widgets for better UI/UX
            'many_to_many': forms.CheckboxSelectMultiple,
            'date_field': forms.DateInput(attrs={'type': 'date'}),
            'time_field': forms.TimeInput(attrs={'type': 'time'}),
            'datetime_field': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }