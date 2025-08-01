from django.shortcuts import render, redirect
from django.http import JsonResponse

#message
from django.contrib import messages

#user
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import  login_required
import re
import string

#auth
from django.contrib.auth import authenticate, login, logout


def home(request):
    return render(request, 'json_app/home.html')


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'json_app/signup.html')

        if not 8 <= len(password1) <= 18:
            messages.error(request, "Password must be between 8 and 18 characters.")
            return render(request, 'json_app/signup.html')

        has_letter = re.search(r'[A-Za-z]', password1)
        has_number = re.search(r'\d', password1)
        has_special = any(char in string.punctuation for char in password1)

        if not (has_letter and has_number and has_special):
            messages.error(request, "Password must include letters, numbers, and special characters.")
            return render(request, 'json_app/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'json_app/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, 'json_app/signup.html')

        user = User.objects.create_user(username=username, password=password1, email=email)

        customer_group, _ = Group.objects.get_or_create(name='Customers')
        user.groups.add(customer_group)

        messages.success(request, "User registered successfully.")
        return redirect('json_app:user_login')

    return render(request, 'json_app/signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, 'json_app/login.html')
        
        user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            return redirect('json_app:home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'json_app/login.html')
    
    logout_msg = request.session.pop('logout_message', None)
    if logout_msg:
        messages.warning(request, logout_msg)
    return render(request, 'json_app/login.html')

@login_required
def profile(request):
    user = request.user
    
    if user.groups.filter(name='Admins').exists():
        role = 'Administrator'
    elif user.groups.filter(name='Customers').exists():
        role = 'Customer'
    else:
        role = 'No role assigned'
    
    user_permissions = []
    for group in user.groups.all():
        for permission in group.permissions.all():
            user_permissions.append(permission.name)
    
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'permissions': user_permissions,
            'is_admin': role == 'Administrator',
            'groups': [group.name for group in user.groups.all()]
        }
        return JsonResponse(data)
    
    context = {
        'user': user,
        'username': user.username,
        'email': user.email,
        'role': role,
        'permissions': user_permissions,
    }
    return render(request, 'json_app/profile.html', context)

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, f"Session closed successfully.")
    return redirect('json_app:user_login')