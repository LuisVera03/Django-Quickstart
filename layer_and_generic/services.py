"""Service layer for layer_and_generic app.

Provides a thin abstraction over repository functions so that:
- Business rules / validation can be inserted without touching views
- Unit tests can target pure functions
- Future cross-cutting concerns (caching, logging, metrics) can hook here

"""

from django.contrib.auth import authenticate, login, logout

# Import functions for data manipulation
from .repositories import (
    create_user, get_user_by_username, 
    get_all_table1, get_table1_by_id, create_table1, update_table1, delete_table1,
    get_all_table2, get_table2_by_id, create_table2, update_table2, delete_table2,
    get_all_table3, get_table3_by_id, create_table3, update_table3, delete_table3
)

#
## Login / Register
#

# Attempts to authenticate and log in a user. Returns True if successful, otherwise False.
def try_login(request, username, password):
    """Authenticate and log in a user.

    Returns True if authentication succeeds, else False.
    """
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return True
    return False

# Registers a new user if the username is not already taken. Returns the created user or None if the username already exists.
def register_user(username, email, password, password_confirm):
    """Register a new user if username not taken.

    password_confirm kept for interface symmetry (could validate match here).
    Returns user instance or None.
    """
    if get_user_by_username(username):
        return None
    return create_user(username, email, password)

#Log out
def perform_logout(request):
    """Safely log out current session."""
    logout(request)

#
## Table1 Services
#

def get_table1_list():
    """Return queryset for Table1 (prefetched via repository)."""
    return get_all_table1()

def get_table1_detail(id):
    """Return single Table1 instance or None."""
    return get_table1_by_id(id)

def create_table1_service(data):
    """Normalize blank strings to None and create Table1 instance."""
    processed_data = data.copy()
    none_fields = ['foreign_key', 'one_to_one', 'integer_field', 'float_field', 
                   'date_field', 'time_field', 'datetime_field']
    
    for field in none_fields:
        if field in processed_data and processed_data[field] == '':
            processed_data[field] = None
    
    return create_table1(processed_data)

def update_table1_service(instance, data):
    """Update Table1 instance normalizing '' -> None for optional fields."""
    processed_data = data.copy()
    none_fields = ['foreign_key', 'one_to_one', 'integer_field', 'float_field', 
                   'date_field', 'time_field', 'datetime_field']
    
    for field in none_fields:
        if field in processed_data and processed_data[field] == '':
            processed_data[field] = None
    
    return update_table1(instance, processed_data)

def delete_table1_service(instance):
    """Delete Table1 instance (repository handles file cleanup)."""
    return delete_table1(instance)

#
## Table2 Services
#

def get_table2_list():
    """Return queryset for Table2."""
    return get_all_table2()

def get_table2_detail(id):
    """Return single Table2 instance or None."""
    return get_table2_by_id(id)

def create_table2_service(data):
    """Create Table2 record."""
    return create_table2(data)

def update_table2_service(instance, data):
    """Update Table2 record."""
    return update_table2(instance, data)

def delete_table2_service(instance):
    """Delete Table2 record."""
    return delete_table2(instance)

#
## Table3 Services
#

def get_table3_list():
    """Return queryset for Table3."""
    return get_all_table3()

def get_table3_detail(id):
    """Return single Table3 instance or None."""
    return get_table3_by_id(id)

def create_table3_service(data):
    """Create Table3 record."""
    return create_table3(data)

def update_table3_service(instance, data):
    """Update Table3 record."""
    return update_table3(instance, data)

def delete_table3_service(instance):
    """Delete Table3 record."""
    return delete_table3(instance)

#
## Dashboard Data
#

def get_dashboard_data():
    """Return aggregate counts for dashboard KPIs."""
    return {
        'total_table1': get_table1_list().count(),
        'total_table2': get_table2_list().count(),
        'total_table3': get_table3_list().count(),
    }