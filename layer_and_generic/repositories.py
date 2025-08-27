"""Repository functions encapsulating direct ORM operations.

- Keep queries optimized (select_related / prefetch_related)
- Centralize transaction boundaries
- Provide clear, minimal interfaces for CRUD

NOTE: Return None when objects are not found instead of raising; service layer decides.
"""

from django.contrib.auth.models import User
from django.db import transaction
from rest.models import Table1, Table2, Table3

# User
def get_user_by_username(username):
    """Return first user with given username or None."""
    return User.objects.filter(username=username).first()

@transaction.atomic
def create_user(username, email, password):
    """Create user inside atomic block (ensures consistency)."""
    print("Creating user:", username)
    return User.objects.create_user(username=username, email=email, password=password)

# Table1 repositories
def get_all_table1():
    """Return Table1 queryset with relationships prefetched (performance)."""
    return Table1.objects.select_related('foreign_key', 'one_to_one').prefetch_related('many_to_many')

def get_table1_by_id(id):
    """Return single Table1 by primary key or None."""
    try:
        return Table1.objects.select_related('foreign_key', 'one_to_one').prefetch_related('many_to_many').get(pk=id)
    except Table1.DoesNotExist:
        return None

@transaction.atomic
def create_table1(data):
    """Create Table1 and set many-to-many if provided."""
    many_to_many_ids = data.pop('many_to_many', [])
    instance = Table1.objects.create(**data)
    if many_to_many_ids:
        instance.many_to_many.set(many_to_many_ids)
    return instance

@transaction.atomic
def update_table1(instance, data):
    """Update fields on Table1 instance; resets many-to-many if list provided."""
    many_to_many_ids = data.pop('many_to_many', None)
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    if many_to_many_ids is not None:
        instance.many_to_many.set(many_to_many_ids)
    return instance

@transaction.atomic
def delete_table1(instance):
    """Delete Table1 ensuring related file fields are removed from storage."""
    if instance.image_field:
        instance.image_field.delete(save=False)
    if instance.file_field:
        instance.file_field.delete(save=False)
    instance.delete()
    return True

# Table2 repositories
def get_all_table2():
    """Return all Table2 objects."""
    return Table2.objects.all()

def get_table2_by_id(id):
    """Return Table2 by primary key or None."""
    try:
        return Table2.objects.get(pk=id)
    except Table2.DoesNotExist:
        return None

@transaction.atomic
def create_table2(data):
    """Create Table2 instance."""
    return Table2.objects.create(**data)

@transaction.atomic
def update_table2(instance, data):
    """Update Table2 fields in-place."""
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance

@transaction.atomic
def delete_table2(instance):
    """Delete Table2 instance."""
    instance.delete()
    return True

# Table3 repositories
def get_all_table3():
    """Return all Table3 objects."""
    return Table3.objects.all()

def get_table3_by_id(id):
    """Return Table3 by primary key or None."""
    try:
        return Table3.objects.get(pk=id)
    except Table3.DoesNotExist:
        return None

@transaction.atomic
def create_table3(data):
    """Create Table3 instance."""
    return Table3.objects.create(**data)

@transaction.atomic
def update_table3(instance, data):
    """Update Table3 fields in-place."""
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance

@transaction.atomic
def delete_table3(instance):
    """Delete Table3 instance."""
    instance.delete()
    return True