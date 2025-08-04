from django.shortcuts import render, redirect, get_object_or_404
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
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from rest_basic.models import Table1, Table2, Table3
import json
import base64
from django.db import transaction
from django.db.models import Prefetch
from django.forms.models import model_to_dict

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
        return redirect('user_login')

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
            return redirect('home')
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
    return redirect('user_login')

@csrf_exempt
def table1_crud(request):
    if request.method == 'GET':
        return table1_crud_get(request)
    elif request.method == 'POST':
        return table1_crud_post(request)
    elif request.method == 'PUT':
        return table1_crud_put(request)
    elif request.method == 'DELETE':
        return table1_crud_delete(request)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def table1_crud_get(request):
    """Handles GET requests for Table1 objects."""
    # Prefetch related objects to reduce database queries
    table1_objects = Table1.objects.all().prefetch_related(
        'many_to_many',
        'foreign_key',
        'one_to_one'
    )

    items = []
    for obj in table1_objects:
        item_dict = {
            field.name: getattr(obj, field.name) if field.name not in ['image_field', 'file_field'] else (obj.get_file_field_url(field.name) if getattr(obj, field.name) else None)
            for field in obj._meta.fields
        }

        # Serialize related fields
        item_dict['foreign_key'] = {'id': obj.foreign_key.id, 'positive_small_int': obj.foreign_key.positive_small_int} if obj.foreign_key else None
        item_dict['one_to_one'] = {'id': obj.one_to_one.id, 'positive_small_int': obj.one_to_one.positive_small_int} if obj.one_to_one else None
        item_dict['many_to_many'] = list(obj.many_to_many.values('id', 'email_field'))

        items.append(item_dict)

    # Get options for select fields
    table2_options = list(Table2.objects.all().values('id', 'positive_small_int'))
    table3_options = list(Table3.objects.all().values('id', 'email_field'))

    return JsonResponse({
        'data': items,
        'table2_options': table2_options,
        'table3_options': table3_options
    }, safe=False)

def table1_crud_post(request):
    """Handles POST requests for creating Table1 objects."""
    return handle_table1_crud(request, None)

def table1_crud_put(request):
    """Handles PUT requests for updating Table1 objects."""
    try:
        data = json.loads(request.body)
        obj_id = data.get('id')
        if not obj_id:
            return JsonResponse({'error': 'ID is required for PUT requests'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return handle_table1_crud(request, obj_id)

def table1_crud_delete(request):
    """Handles DELETE requests for deleting Table1 objects."""
    try:
        data = json.loads(request.body)
        entry = get_object_or_404(Table1, id=data['id'])
        # Delete associated files if they exist
        if entry.image_field:
            entry.image_field.delete(save=False)
        if entry.file_field:
            entry.file_field.delete(save=False)
        entry.delete()
        return JsonResponse({'message': 'Deleted'}, status=204)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Table1.DoesNotExist:
        return JsonResponse({'error': 'Object not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def handle_table1_crud(request, obj_id):
    """Handles both POST and PUT requests for Table1 objects."""
    try:
        if request.FILES:
            data = json.loads(request.POST.get('data', '{}'))
            files_data = request.FILES
        else:
            data = json.loads(request.body)
            files_data = {}

        # Handle base64 files
        for field in ['image_field', 'file_field']:
            file_info = data.pop(field, None)
            if file_info and isinstance(file_info, dict) and 'content' in file_info and 'name' in file_info:
                try:
                    format, imgstr = file_info['content'].split(';base64,')
                    file_content = ContentFile(base64.b64decode(imgstr), name=file_info['name'])
                    files_data[field] = file_content
                except ValueError:
                    return JsonResponse({'error': f'Invalid base64 data for {field}'}, status=400)

        # Handle foreign key relationships
        foreign_key_id = data.pop('foreign_key', {}).get('id') if 'foreign_key' in data else None
        one_to_one_id = data.pop('one_to_one', {}).get('id') if 'one_to_one' in data else None
        many_to_many_ids = [item['id'] for item in data.pop('many_to_many', [])]

        # Get or create the object
        if obj_id:
            try:
                obj = Table1.objects.get(id=obj_id)
                # Clear existing many-to-many relationships
                obj.many_to_many.clear()
                # Delete associated files if new files are uploaded
                for field in ['image_field', 'file_field']:
                    if field in files_data and getattr(obj, field):
                        getattr(obj, field).delete(save=False)
            except Table1.DoesNotExist:
                return JsonResponse({'error': 'Object not found'}, status=404)
        else:
            obj = Table1()

        # Update basic fields
        for key, value in data.items():
            setattr(obj, key, value)

        # Handle file uploads
        for field, file in files_data.items():
             setattr(obj, field, file)

        # Handle relationships
        obj.foreign_key = Table2.objects.get(id=foreign_key_id) if foreign_key_id else None
        obj.one_to_one = Table2.objects.get(id=one_to_one_id) if one_to_one_id else None

        with transaction.atomic():
            obj.save()
            obj.many_to_many.set(Table3.objects.filter(id__in=many_to_many_ids))

        # Prepare response data
        response_data = {
            'id': obj.id,
            'image_field': obj.get_file_field_url('image_field'),
            'file_field':  obj.get_file_field_url('file_field'),
            'foreign_key': {'id': obj.foreign_key.id, 'positive_small_int': obj.foreign_key.positive_small_int} if obj.foreign_key else None,
            'one_to_one': {'id': obj.one_to_one.id, 'positive_small_int': obj.one_to_one.positive_small_int} if obj.one_to_one else None,
            'many_to_many': list(obj.many_to_many.values('id', 'email_field'))
        }

        status_code = 200 if obj_id else 201
        return JsonResponse({'data': response_data}, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Table2.DoesNotExist:
        return JsonResponse({'error': 'Table2 object not found'}, status=400)
    except Table3.DoesNotExist:
        return JsonResponse({'error': 'Table3 object not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def table2_crud(request):
    if request.method == 'GET':
        items = list(Table2.objects.all().values())
        return JsonResponse({'data': items}, status=200)
    elif request.method == 'POST':
        data = json.loads(request.body)
        obj = Table2.objects.create(**data)
        return JsonResponse({'data': model_to_dict(obj)}, status=201)
    elif request.method == 'PUT':
        data = json.loads(request.body)
        obj = Table2.objects.get(id=data['id'])
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return JsonResponse({'data': model_to_dict(obj)}, status=200)
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        Table2.objects.filter(id=data['id']).delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

@csrf_exempt
def table3_crud(request):
    if request.method == 'GET':
        items = list(Table3.objects.all().values())
        return JsonResponse({'data': items}, status=200)
    elif request.method == 'POST':
        data = json.loads(request.body)
        obj = Table3.objects.create(**data)
        return JsonResponse({'data': model_to_dict(obj)}, status=201)
    elif request.method == 'PUT':
        data = json.loads(request.body)
        obj = Table3.objects.get(id=data['id'])
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return JsonResponse({'data': model_to_dict(obj)}, status=200)
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        Table3.objects.filter(id=data['id']).delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

