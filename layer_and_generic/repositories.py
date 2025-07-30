from django.contrib.auth.models import User
from django.db import transaction
from rest_basic.models import Table1, Table2, Table3

# User
def get_user_by_username(username):
    return User.objects.filter(username=username).first()

@transaction.atomic
def create_user(username, email, password):
    print("Creating user:", username)
    return User.objects.create_user(username=username, email=email, password=password)

# Table1 repositories
def get_all_table1():
    return Table1.objects.select_related('foreign_key', 'one_to_one').prefetch_related('many_to_many')

def get_table1_by_id(id):
    try:
        return Table1.objects.select_related('foreign_key', 'one_to_one').prefetch_related('many_to_many').get(pk=id)
    except Table1.DoesNotExist:
        return None

@transaction.atomic
def create_table1(data):
    many_to_many_ids = data.pop('many_to_many', [])
    instance = Table1.objects.create(**data)
    if many_to_many_ids:
        instance.many_to_many.set(many_to_many_ids)
    return instance

@transaction.atomic
def update_table1(instance, data):
    many_to_many_ids = data.pop('many_to_many', None)
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    if many_to_many_ids is not None:
        instance.many_to_many.set(many_to_many_ids)
    return instance

@transaction.atomic
def delete_table1(instance):
    if instance.image_field:
        instance.image_field.delete(save=False)
    if instance.file_field:
        instance.file_field.delete(save=False)
    instance.delete()
    return True

# Table2 repositories
def get_all_table2():
    return Table2.objects.all()

def get_table2_by_id(id):
    try:
        return Table2.objects.get(pk=id)
    except Table2.DoesNotExist:
        return None

@transaction.atomic
def create_table2(data):
    return Table2.objects.create(**data)

@transaction.atomic
def update_table2(instance, data):
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance

@transaction.atomic
def delete_table2(instance):
    instance.delete()
    return True

# Table3 repositories
def get_all_table3():
    return Table3.objects.all()

def get_table3_by_id(id):
    try:
        return Table3.objects.get(pk=id)
    except Table3.DoesNotExist:
        return None

@transaction.atomic
def create_table3(data):
    return Table3.objects.create(**data)

@transaction.atomic
def update_table3(instance, data):
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance

@transaction.atomic
def delete_table3(instance):
    instance.delete()
    return True