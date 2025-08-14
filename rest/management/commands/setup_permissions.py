from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from rest.models import Table1, Table2, Table3

class Command(BaseCommand):
    help = 'Setup groups and permissions for the application'

    def handle(self, *args, **options):
        # Create groups
        customer_group, created = Group.objects.get_or_create(name='Customers')
        admin_group, created = Group.objects.get_or_create(name='Admins')
        
        # Get content type for the app (use Table1 as reference, but these will be app-level permissions)
        app_content_type = ContentType.objects.get_for_model(Table1)
        
        # Create app-level permissions that work with all tables
        view_data_perm, created = Permission.objects.get_or_create(
            codename='view_data',
            name='Can view all data',
            content_type=app_content_type,
        )
        add_data_perm, created = Permission.objects.get_or_create(
            codename='add_data',
            name='Can add data',
            content_type=app_content_type,
        )
        change_data_perm, created = Permission.objects.get_or_create(
            codename='change_data',
            name='Can change data',
            content_type=app_content_type,
        )
        delete_data_perm, created = Permission.objects.get_or_create(
            codename='delete_data',
            name='Can delete data',
            content_type=app_content_type,
        )
        manage_users_perm, created = Permission.objects.get_or_create(
            codename='manage_users',
            name='Can manage users',
            content_type=app_content_type,
        )
        
        # Assign permissions to groups
        # Customers only get view permissions
        customer_group.permissions.set([view_data_perm])
        
        # Admins get all permissions
        all_admin_permissions = [
            view_data_perm, 
            add_data_perm, 
            change_data_perm, 
            delete_data_perm, 
            manage_users_perm
        ]
        admin_group.permissions.set(all_admin_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and permissions')
        )