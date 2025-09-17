from django import forms
import re
from rest.models import Table1, Table2, Table3

# Forms for user login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# Forms for user register
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    def clean (self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
        if not (8 <= len(password) <= 14):
            self.add_error('password', "Password must be between 8 and 14 characters long.")
        elif not re.search(r'[A-Z]', password):
            self.add_error('password', "Password must contain at least one uppercase letter.")
        elif not re.search(r'\d', password):
            self.add_error('password', "Password must contain at least one number.")
        elif not re.search(r'[^\w\s]', password):
            self.add_error('password', "Password must contain at least one special character.")
        
        return cleaned_data
    
class Table1Form(forms.ModelForm):
    class Meta:
        model = Table1
        fields = [
            'char_field', 'text_field', 'boolean_field',
            'integer_field', 'float_field', 'date_field',
            'time_field', 'datetime_field', 'image_field',
            'file_field', 'foreign_key', 'one_to_one', 'many_to_many'
        ]
        widgets = {
            'char_field': forms.TextInput(attrs={'class': 'form-control'}),
            'text_field': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'boolean_field': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'integer_field': forms.NumberInput(attrs={'class': 'form-control'}),
            'float_field': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_field': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_field': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'datetime_field': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'image_field': forms.FileInput(attrs={'class': 'form-control'}),
            'file_field': forms.FileInput(attrs={'class': 'form-control'}),
            'foreign_key': forms.Select(attrs={'class': 'form-control'}),
            'one_to_one': forms.Select(attrs={'class': 'form-control'}),
            'many_to_many': forms.CheckboxSelectMultiple(),
        }

class Table2Form(forms.ModelForm):
    class Meta:
        model = Table2
        fields = '__all__'
        widgets = {
            'char_field': forms.TextInput(attrs={'class': 'form-control'}),
            'text_field': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'boolean_field': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'integer_field': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class Table3Form(forms.ModelForm):
    class Meta:
        model = Table3
        fields = '__all__'
        widgets = {
            'char_field': forms.TextInput(attrs={'class': 'form-control'}),
            'text_field': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'boolean_field': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'integer_field': forms.NumberInput(attrs={'class': 'form-control'}),
        }