from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Table3(models.Model):
    # Stores a time duration (e.g., 5 days, 3 hours)
    duration_field = models.DurationField()

    # Stores a valid email address (with built-in validation)
    email_field = models.EmailField(max_length=254, unique=True)
    
    def __str__(self):
        return f"Table3 ID: {self.id}"


class Table2(models.Model):
    # Choices for a small positive integer field
    CHOICES = (
        (1, 'option1'),
        (2, 'option2'),
    )
    positive_small_int = models.PositiveSmallIntegerField(choices=CHOICES, default=1)

    def __str__(self):
        return f"Table2 ID: {self.id}"


class Table1(models.Model):
    # Relationships to Table2
    foreign_key = models.ForeignKey(Table2, on_delete=models.CASCADE, related_name='table1_foreign', null=True, blank=True)
    one_to_one = models.OneToOneField(Table2, on_delete=models.CASCADE, related_name='table1_one', null=True, blank=True)
    many_to_many = models.ManyToManyField(Table3, related_name='table1_many', blank=True)

    # Basic fields
    integer_field = models.IntegerField(null=True, blank=True)      # Integer value (optional)
    float_field = models.FloatField(null=True, blank=True)          # Floating point number
    char_field = models.CharField(max_length=15)                    # Short text with max length
    text_field= models.TextField(blank=True)                        # Long text (optional)
    boolean_field = models.BooleanField(default=False)              # True or False

    # Date and time fields
    date_field = models.DateField(null=True, blank=True)           # Date only
    time_field = models.TimeField(null=True, blank=True)           # Time only
    datetime_field = models.DateTimeField(null=True, blank=True)   # Full date and time

    # File and image uploads
    image_field = models.ImageField(upload_to='images/', null=True, blank=True)  # For image files
    file_field = models.FileField(upload_to='files/', null=True, blank=True)     # For general files

    def __str__(self):
        return f"Table1 ID: {self.id}"
    
    def get_file_field_url(self, field_name):
        file_field = getattr(self, field_name)
        return file_field.url if file_field else None
    
class UserLog(models.Model):
    EVENT_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=150)  
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True) 

    def __str__(self):
        return f"[{self.timestamp}] {self.username} - {self.get_event_type_display()}"