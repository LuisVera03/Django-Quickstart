from django import forms
import re
from rest_basic.models import Table1

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
            'file_field'
        ]
        widgets = {
            'date_field': forms.DateInput(attrs={'type': 'date'}),
            'time_field': forms.TimeInput(attrs={'type': 'time'}),
            'datetime_field': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class Table1Form(forms.ModelForm):
    class Meta:
        model = Table1
        fields = [
            'char_field', 'text_field', 'boolean_field',
            'integer_field', 'float_field', 'date_field',
            'time_field', 'datetime_field', 'image_field',
            'file_field'
        ]
        widgets = {
            'date_field': forms.DateInput(attrs={'type': 'date'}),
            'time_field': forms.TimeInput(attrs={'type': 'time'}),
            'datetime_field': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
