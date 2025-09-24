"""Repository classes encapsulating direct ORM operations.

- Keep queries optimized (select_related / prefetch_related)
- Centralize transaction boundaries
- Provide clear, minimal interfaces for CRUD
"""

from django.contrib.auth.models import User
from django.db import transaction
from rest.models import Table1, Table2, Table3


# ======================
# Generic Repository
# ======================
class BaseRepository:
    model = None  # <- override in each repository

    @classmethod
    def get_all(cls):
        """Return all objects of model."""
        return cls.model.objects.all()

    @classmethod
    def get_by_id(cls, id):
        """Return single object or None."""
        try:
            return cls.model.objects.get(pk=id)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    @transaction.atomic
    def create(cls, data):
        """Create instance with dict of fields."""
        return cls.model.objects.create(**data)

    @classmethod
    @transaction.atomic
    def update(cls, instance, data):
        """Update fields in instance and save."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    @classmethod
    @transaction.atomic
    def delete(cls, instance):
        """Delete instance safely."""
        instance.delete()
        return True


# ======================
# User Repository
# ======================
class UserRepository:
    @staticmethod
    def get_by_username(username):
        return User.objects.filter(username=username).first()

    @staticmethod
    @transaction.atomic
    def create_user(username, email, password):
        return User.objects.create_user(
            username=username, email=email, password=password
        )


# ======================
# Table1 Repository
# ======================
class Table1Repository(BaseRepository):
    model = Table1

    @classmethod
    def get_all(cls):
        """Optimized queryset for Table1."""
        return cls.model.objects.select_related(
            "foreign_key", "one_to_one"
        ).prefetch_related("many_to_many")

    @classmethod
    def get_by_id(cls, id):
        try:
            return (
                cls.model.objects.select_related("foreign_key", "one_to_one")
                .prefetch_related("many_to_many")
                .get(pk=id)
            )
        except cls.model.DoesNotExist:
            return None

    @classmethod
    @transaction.atomic
    def create(cls, data):
        """Handle many-to-many creation."""
        many_to_many_ids = data.pop("many_to_many", [])
        instance = cls.model.objects.create(**data)
        if many_to_many_ids:
            instance.many_to_many.set(many_to_many_ids)
        return instance

    @classmethod
    @transaction.atomic
    def update(cls, instance, data):
        """Handle many-to-many updates."""
        many_to_many_ids = data.pop("many_to_many", None)
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        if many_to_many_ids is not None:
            instance.many_to_many.set(many_to_many_ids)
        return instance

    @classmethod
    @transaction.atomic
    def delete(cls, instance):
        """Delete with cleanup for file fields."""
        if getattr(instance, "image_field", None):
            instance.image_field.delete(save=False)
        if getattr(instance, "file_field", None):
            instance.file_field.delete(save=False)
        instance.delete()
        return True

# ======================
# Table2 Repository
# ======================
class Table2Repository(BaseRepository):
    model = Table2
# ======================
# Table3 Repository
# ======================
class Table3Repository(BaseRepository):
    model = Table3
