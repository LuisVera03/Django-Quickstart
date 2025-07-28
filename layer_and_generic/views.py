from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm, RegisterForm, Table1Form
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Messages
from django.contrib import messages

from .services import try_login, register_user, perform_logout

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_basic.models import Table1
#
## Login / Register
#

# Handle user login.

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = LoginForm()
        return render(request, 'LAG/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            success = try_login(request, **form.cleaned_data)
            if success:
                return redirect('home')
            else:
                messages.error(request, "Incorrect username or password")
        return render(request, 'LAG/login.html', {'form': form})

# Handles user registration.
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'LAG/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():

            user = register_user(**form.cleaned_data)
            if user:
                messages.success(request, "User created successfully")
                return redirect('login')
            else:
                messages.error(request, "User alredy exists")

        return render(request, 'LAG/register.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        perform_logout(request)
        return redirect('login')

# Para vistas basadas en función
@login_required
def home(request):
    return render(request, 'LAG/home.html')

# Para vistas basadas en clase
@method_decorator(login_required, name='dispatch')
class Table1ListView(ListView):
    model = Table1
    template_name = 'list.html'
    context_object_name = 'table1_list'

@method_decorator(login_required, name='dispatch')
class Table1DetailView(DetailView):
    model = Table1
    template_name = 'detail.html'
    context_object_name = 'table1'

@method_decorator(login_required, name='dispatch')
class Table1CreateView(CreateView):
    model = Table1
    template_name = 'form.html'
    form_class = Table1Form
    success_url = reverse_lazy('list')

@method_decorator(login_required, name='dispatch')
class Table1UpdateView(UpdateView):
    model = Table1
    template_name = 'form.html'
    form_class = Table1Form
    success_url = reverse_lazy('list')

@method_decorator(login_required, name='dispatch')
class Table1DeleteView(DeleteView):
    model = Table1
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('list')