"""Views for json_app: authentication, profile, and JSON-based CRUD endpoints.

This module exposes:
1. User auth flows (register, login, logout, profile)
2. Hybrid HTML/JSON profile response
3. REST-like CRUD endpoints for Table1/Table2/Table3 (returning JSON only)
4. Search endpoints for bulk retrieval (optimized with prefetch/select)
5. File & image handling supporting multipart and base64 payloads

Design notes:
- Endpoints are intentionally CSRF-exempt for JSON clients (could be tightened with tokens)
- Pagination logic caps page_size to protect the DB and prevent abuse (1..100)
- Relationship fields are normalized in responses to stable id+label objects
- File update replaces old file safely and avoids orphan files
"""

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
from rest.models import Table1, Table2, Table3
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import base64
from django.db import transaction
from django.db.models import Prefetch
from django.forms.models import model_to_dict
from datetime import timedelta

# Home view (simple template render)
def home(request):
    return render(request, 'json_app/home.html')

# User registration and login views
def user_register(request):
    """Register a new user.

    Validation:
    - Password confirmation
    - Length (8..18 chars)
    - Composition: at least one letter, one digit, one punctuation char
    - Unique username & email
    On success: user is created and added to 'Customers' group.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validate input
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'json_app/signup.html')

        # Check password strength
        if not 8 <= len(password1) <= 18:
            messages.error(request, "Password must be between 8 and 18 characters.")
            return render(request, 'json_app/signup.html')

        # Check for letters, numbers, and special characters
        has_letter = re.search(r'[A-Za-z]', password1)
        has_number = re.search(r'\d', password1)
        has_special = any(char in string.punctuation for char in password1)

        # If any of the conditions are not met, return an error message
        if not (has_letter and has_number and has_special):
            messages.error(request, "Password must include letters, numbers, and special characters.")
            return render(request, 'json_app/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'json_app/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, 'json_app/signup.html')

        # Create the user
        user = User.objects.create_user(username=username, password=password1, email=email)
        customer_group, _ = Group.objects.get_or_create(name='Customers')
        user.groups.add(customer_group)

        messages.success(request, "User registered successfully.")
        return redirect('login_json')

    return render(request, 'json_app/signup.html')

def user_login(request):
    """Authenticate user credentials and start session."""
    if request.method == 'POST':
        # Get username and password from the request
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validate input
        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, 'json_app/login.html')
        
        user = authenticate(request, username=username, password=password)

        # If authentication is successful, log the user in    
        if user is not None:
            login(request, user)
            # Save current app in session
            request.session['current_app'] = 'json_app'
            request.session['home_url'] = 'home_json'
            request.session['logout_url'] = 'logout_json'
            return redirect('home_json')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'json_app/login.html')
        
    # If the request method is not POST, render the login page
    logout_msg = request.session.pop('logout_message', None)
    if logout_msg:
        messages.warning(request, logout_msg)
    return render(request, 'json_app/login.html')

# Profile view to display user information and permissions
@login_required
def profile(request):
    """Return profile info."""
    # Get the logged-in user
    user = request.user

    # Determine the user's role based on group membership
    if user.groups.filter(name='Admins').exists():
        role = 'Administrator'
    elif user.groups.filter(name='Customers').exists():
        role = 'Customer'
    else:
        role = 'No role assigned'
    
    # Get user permissions
    user_permissions = []
    for group in user.groups.all():
        for permission in group.permissions.all():
            user_permissions.append(permission.name)
    
    # Remove duplicates and sort permissions
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
    
    # Render the profile page with user information
    context = {
        'user': user,
        'username': user.username,
        'email': user.email,
        'role': role,
        'permissions': user_permissions,
    }
    return render(request, 'json_app/profile.html', context)

# Logout view to handle user logout
@login_required
def user_logout(request):
    """Invalidate user session via POST (idempotent)."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, f"Session closed successfully.")
        return redirect('login_json')

# CRUD views for Table1
@csrf_exempt
def table1_crud(request):
    """Multi-method endpoint dispatching CRUD operations for Table1."""
    if request.method == 'GET':
        return table1_crud_get(request)
    if request.method == 'POST':
        return table1_crud_post(request)
    if request.method == 'PUT':
        return table1_crud_put(request)
    if request.method == 'DELETE':
        return table1_crud_delete(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Handles GET requests for Table1 objects with pagination
def table1_crud_get(request):
    """Return paginated Table1 objects with related data & option lists."""
    # Parse pagination parameters - defaults to page 1 with 5 items per page
    page = request.GET.get('page', 1)
    raw_page_size = request.GET.get('page_size', 5)
    try:
        page_size = int(raw_page_size)
    except (TypeError, ValueError):
        page_size = 5
    # Enforce reasonable limits for page size
    if page_size < 1:
        page_size = 5
    if page_size > 100:
        page_size = 100

    # Explicit ordering prevents UnorderedObjectListWarning
    queryset = Table1.objects.all().order_by('id').prefetch_related('many_to_many', 'foreign_key', 'one_to_one')
    total = queryset.count()
    
    # Only enable pagination if we have 5 or more items
    if total >= 5:
        # Use Django's Paginator for proper pagination handling
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
            page = 1
        except EmptyPage:
            # If page is out of range, return last page
            page_obj = paginator.page(paginator.num_pages)
            page = paginator.num_pages
        
        items = _serialize_table1_objects(page_obj.object_list)
        pagination_payload = {
            'enabled': True,
            'page': int(page),
            'page_size': page_size,
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    else:
        # Return all items without pagination for small datasets
        items = _serialize_table1_objects(queryset)
        pagination_payload = {'enabled': False, 'total_items': total}

    # Get options for foreign key and many-to-many fields
    table2_options = list(Table2.objects.all().values('id', 'positive_small_int'))
    table3_options = list(Table3.objects.all().values('id', 'email_field'))

    return JsonResponse({
        'data': items,
        'pagination': pagination_payload,
        'table2_options': table2_options,
        'table3_options': table3_options
    })


def _serialize_table1_objects(queryset):
    """Serialize Table1 queryset into list of dicts."""
    items = []
    for obj in queryset:
        # Handle file fields specially to get proper URLs
        item_dict = {
            field.name: (
                getattr(obj, field.name) 
                if field.name not in ['image_field', 'file_field'] 
                else obj.get_file_field_url(field.name) if getattr(obj, field.name) else None
            )
            for field in obj._meta.fields
        }
        
        # Serialize relationship fields with proper structure
        item_dict['foreign_key'] = (
            {'id': obj.foreign_key.id, 'positive_small_int': obj.foreign_key.positive_small_int} 
            if obj.foreign_key else None
        )
        item_dict['one_to_one'] = (
            {'id': obj.one_to_one.id, 'positive_small_int': obj.one_to_one.positive_small_int} 
            if obj.one_to_one else None
        )
        item_dict['many_to_many'] = list(obj.many_to_many.values('id', 'email_field'))
        items.append(item_dict)
    return items

# Handles POST requests for creating Table1 objects
def table1_crud_post(request):
    """Create a Table1 record (multipart or JSON)."""
    return handle_table1_crud(request, None)

# Handles PUT requests for updating Table1 objects
def table1_crud_put(request):
    """Update a Table1 record (requires id in JSON body)."""
    # Check if the request body contains an ID
    try:
        data = json.loads(request.body)
        obj_id = data.get('id')
        if not obj_id:
            return JsonResponse({'error': 'ID is required for PUT requests'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return handle_table1_crud(request, obj_id)

# Handles both POST and PUT requests for Table1 objects
def handle_table1_crud(request, obj_id):
    """Shared create/update logic.

    Supports two payload modes:
    1. Multipart form-data with 'data' JSON chunk + files
    2. Raw JSON body containing everything possibly including base64 file objects

    Base64 file object format:
        { "image_field": {"name": "foo.png", "content": "data:image/png;base64,..."} }

    Relationship payload expectations:
        foreign_key: {"id": int} or null
        one_to_one:  {"id": int} or null
        many_to_many: [{"id": int}, ...]
    """
    try:
        # Check if the request contains files or JSON data
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

        # Handle relationship payloads safely to prevent AttributeError
        # Extract foreign key ID if payload is a valid dict, otherwise set to None
        fk_payload = data.pop('foreign_key', None)
        foreign_key_id = fk_payload.get('id') if isinstance(fk_payload, dict) else None

        # Extract one-to-one relationship ID safely
        oto_payload = data.pop('one_to_one', None)
        one_to_one_id = oto_payload.get('id') if isinstance(oto_payload, dict) else None

        # Extract many-to-many IDs from list of objects, ensuring safety
        m2m_payload = data.pop('many_to_many', [])
        if not isinstance(m2m_payload, list):
            m2m_payload = []
        many_to_many_ids = [
            item.get('id') for item in m2m_payload 
            if isinstance(item, dict) and 'id' in item
        ]

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
    
    # Handle exceptions
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Table2.DoesNotExist:
        return JsonResponse({'error': 'Table2 object not found'}, status=400)
    except Table3.DoesNotExist:
        return JsonResponse({'error': 'Table3 object not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# Handles DELETE requests for deleting Table1 objects
def table1_crud_delete(request):
    """Delete a Table1 record including associated files (if any)"""
    # Check if the request body contains an ID
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

# Helper function to handle paginated GET requests for simple models
def _handle_simple_table_get(model_class, request):
    """
    Generic pagination handler for simple CRUD operations.
    
    Returns:
        JsonResponse with paginated data and pagination metadata
    """
    page = request.GET.get('page', 1)
    raw_page_size = request.GET.get('page_size', 5)
    
    # Validate and sanitize page size parameter
    try:
        page_size = int(raw_page_size)
    except (TypeError, ValueError):
        page_size = 5
    
    # Enforce page size limits for performance and usability
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    # Explicit ordering to prevent UnorderedObjectListWarning
    queryset = model_class.objects.all().order_by('id')
    total = queryset.count()
    
    # Enable pagination only when there are 5 or more records
    if total >= 5:
        paginator = Paginator(queryset, page_size)
        
        # Handle page validation and edge cases
        try:
            page_obj = paginator.page(page)
            page_number = int(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
            page_number = 1
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            page_number = paginator.num_pages
        
        items = list(page_obj.object_list.values())
        pagination_payload = {
            'enabled': True,
            'page': page_number,
            'page_size': page_size,
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    else:
        # Return all items without pagination for small datasets
        items = list(queryset.values())
        pagination_payload = {'enabled': False, 'total_items': total}
    
    return JsonResponse({'data': items, 'pagination': pagination_payload}, status=200)

# CRUD views for Table2 and Table3
@csrf_exempt
def table2_crud(request):
    """JSON CRUD + pagination for Table2."""
    if request.method == 'GET':
        return _handle_simple_table_get(Table2, request)
    elif request.method == 'POST':
        # Create a new Table2 object
        data = json.loads(request.body)
        obj = Table2.objects.create(**data)
        return JsonResponse({'data': model_to_dict(obj)}, status=201)
    elif request.method == 'PUT':
        # Update an existing Table2 object
        data = json.loads(request.body)
        obj = Table2.objects.get(id=data['id'])
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return JsonResponse({'data': model_to_dict(obj)}, status=200)
    elif request.method == 'DELETE':
        # Delete a Table2 object
        data = json.loads(request.body)
        Table2.objects.filter(id=data['id']).delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

@csrf_exempt
def table3_crud(request):
    """JSON CRUD + pagination for Table3 (same pattern as Table2)."""
    if request.method == 'GET':
        return _handle_simple_table_get(Table3, request)
    elif request.method == 'POST':
        # Create a new Table3 object
        data = json.loads(request.body)
        
        # Convert duration string to timedelta if present
        if 'duration_field' in data:
            duration_str = data['duration_field']
            print(duration_str)
            # Parse duration string in format "DD HH:MM:SS" or "HH:MM:SS"
            try:
                if ' ' in duration_str:
                    days_str, time_str = duration_str.split(' ')
                    days = int(days_str)
                else:
                    time_str = duration_str
                    days = 0
                    
                hours, minutes, seconds = map(int, time_str.split(':'))
                data['duration_field'] = timedelta(
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds
                )
            except (ValueError, AttributeError) as e:
                return JsonResponse({'error': 'Invalid duration format. Use "DD HH:MM:SS" or "HH:MM:SS"'}, status=400)
                
        obj = Table3.objects.create(**data)
        return JsonResponse({'data': model_to_dict(obj)}, status=201)
    elif request.method == 'PUT':
        # Update an existing Table3 object
        data = json.loads(request.body)
        obj = Table3.objects.get(id=data['id'])
        
        # Convert duration string to timedelta if present
        if 'duration_field' in data:
            duration_str = data['duration_field']
            try:
                if ' ' in duration_str:
                    days_str, time_str = duration_str.split(' ')
                    days = int(days_str)
                else:
                    time_str = duration_str
                    days = 0
                    
                hours, minutes, seconds = map(int, time_str.split(':'))
                data['duration_field'] = timedelta(
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds
                )
            except (ValueError, AttributeError) as e:
                return JsonResponse({'error': 'Invalid duration format. Use "DD HH:MM:SS" or "HH:MM:SS"'}, status=400)
                
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return JsonResponse({'data': model_to_dict(obj)}, status=200)
    elif request.method == 'DELETE':
        # Delete a Table3 object
        data = json.loads(request.body)
        Table3.objects.filter(id=data['id']).delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

# Search view to render the search page
@login_required
def search_view(request):
    """Render the search interface HTML (AJAX front-end consumes JSON endpoints)."""
    return render(request, 'json_app/search.html')

# Search view to return all Table1 data in JSON format
@csrf_exempt
@login_required
def search_all_data(request):
    """Return full unpaginated Table1 dataset (for client-side filtering/search).

    WARNING: For very large tables this may be expensive
    """

    if request.method == 'GET':
        # Prefetch related objects to reduce database queries
        queryset = Table1.objects.all().prefetch_related('many_to_many', 'foreign_key', 'one_to_one')
        
        # Serialize the queryset into a list of dictionaries
        items = []
        for obj in queryset:
            item_dict = {
                'id': obj.id,
                'char_field': obj.char_field,
                'text_field': obj.text_field,
                'integer_field': obj.integer_field,
                'float_field': obj.float_field,
                'boolean_field': obj.boolean_field,
                'date_field': obj.date_field.isoformat() if obj.date_field else None,
                'time_field': obj.time_field.isoformat() if obj.time_field else None,
                'datetime_field': obj.datetime_field.isoformat() if obj.datetime_field else None,
                'image_field': obj.get_file_field_url('image_field'),
                'file_field': obj.get_file_field_url('file_field'),
                'foreign_key': {
                    'id': obj.foreign_key.id, 
                    'positive_small_int': obj.foreign_key.positive_small_int,
                    'display': obj.foreign_key.get_positive_small_int_display()
                } if obj.foreign_key else None,
                'one_to_one': {
                    'id': obj.one_to_one.id, 
                    'positive_small_int': obj.one_to_one.positive_small_int,
                    'display': obj.one_to_one.get_positive_small_int_display()
                } if obj.one_to_one else None,
                'many_to_many': list(obj.many_to_many.values('id', 'email_field', 'duration_field'))
            }
            items.append(item_dict)
            
        # Return the serialized data as a JSON response
        return JsonResponse({
            'data': items, 
            'count': len(items),
            'message': 'All data loaded successfully'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)