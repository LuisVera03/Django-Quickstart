from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
#auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_channels')  # o donde quieras
    else:
        form = UserCreationForm()
    return render(request, 'channels/register.html', {'form': form})

class LoginView(LoginView):
    template_name = 'channels/login.html'
    def get_success_url(self):
        return reverse_lazy('home_channels')


@login_required
def logout_channels(request):
    logout(request)
    return render(request, 'channels/home.html')

@login_required
def home_channels(request):
    return render(request, 'channels/home.html')

