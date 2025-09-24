"""
Service layer: applies business logic over repositories.
- Does not directly touch the ORM
- Handles errors and rules
- Orchestrates operations across multiple entities
"""

from django.contrib.auth import authenticate, login, logout
from django.db import models
from .repositories import (
    UserRepository,
    Table1Repository,
    Table2Repository,
    Table3Repository,
)


# ======================
# User Services
# ======================
class UserService:
    @staticmethod
    def register_user(username, email, password):
        """Register a new user."""
        if UserRepository.get_by_username(username):
            raise ValueError("User already exists")
        return UserRepository.create_user(username, email, password)

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate an existing user."""
        return authenticate(username=username, password=password)


# ======================
# Auth helpers (functions used by views)
# ======================
def try_login(request, username, password):
    """Authenticates and performs login. Returns True if successful."""
    user = UserService.authenticate_user(username, password)
    if user is not None:
        login(request, user)
        return True
    return False


def register_user(username, email, password):
    """Simple wrapper to register and return the created user.
    If already exists, returns None so the view can show the message.
    """
    try:
        return UserService.register_user(username, email, password)
    except ValueError:
        return None


def perform_logout(request):
    """Logs out the current session."""
    logout(request)
    return True


# ======================
# Table Services (Generic)
# ======================
class BaseService:
    repository = None  # <- override in each service

    @classmethod
    def list(cls):
        return cls.repository.get_all()

    @classmethod
    def get(cls, id):
        return cls.repository.get_by_id(id)

    # More expressive alias for what views use
    @classmethod
    def detail(cls, id):
        return cls.get(id)

    @classmethod
    def create(cls, **data):
        """Creates an instance from kwargs (compatible with form.cleaned_data)."""
        return cls.repository.create(dict(data))

    @classmethod
    def update(cls, pk, **data):
        """Updates by pk with kwargs (compatible with form.cleaned_data)."""
        instance = cls.repository.get_by_id(pk)
        if not instance:
            raise ValueError("Object not found")
        return cls.repository.update(instance, dict(data))

    @classmethod
    def delete(cls, pk):
        instance = cls.repository.get_by_id(pk)
        if not instance:
            raise ValueError("Object not found")
        return cls.repository.delete(instance)

    @classmethod
    def get_field_data(cls, instance):
        """Returns a list of dictionaries with field name and value."""
        if not instance:
            return []

        fields = []
        # Obtain all model fields
        for field in instance._meta.fields:
            if field.name == "id":
                continue

            value = getattr(instance, field.name)
            # Handle special cases
            if field.choices:
                # If the field has choices, get the readable value
                value = getattr(instance, f"get_{field.name}_display")()
            elif field.is_relation:
                # If it's a relation, get the str of the related object
                value = str(value) if value else None
            elif isinstance(field, (models.FileField, models.ImageField)):
                # For file fields, get the URL
                value = value.url if value else None

            fields.append(
                {
                    "name": field.verbose_name or field.name.replace("_", " ").title(),
                    "value": value if value is not None else "-",
                }
            )

        # Handle ManyToMany fields
        for field in instance._meta.many_to_many:
            related_objects = getattr(instance, field.name).all()
            value = (
                ", ".join([str(obj) for obj in related_objects])
                if related_objects.exists()
                else "-"
            )
            fields.append(
                {
                    "name": field.verbose_name or field.name.replace("_", " ").title(),
                    "value": value,
                }
            )

        return fields


class Table1Service(BaseService):
    repository = Table1Repository


class Table2Service(BaseService):
    repository = Table2Repository


class Table3Service(BaseService):
    repository = Table3Repository


# ======================
# Dashboard data
# ======================
def get_dashboard_data():
    """Returns simple metrics for LAG Home."""
    return {
        "table1_count": Table1Repository.get_all().count(),
        "table2_count": Table2Repository.get_all().count(),
        "table3_count": Table3Repository.get_all().count(),
    }
