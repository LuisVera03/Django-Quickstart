from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.models import User
from .models import UserLog
from django.utils.timezone import now

# Helper function to get client IP address
def get_client_ip(request):
    """Return client IP safely. request can be None in some signals (e.g., user_login_failed)."""
    if request is None:
        return "unknown"
    meta = getattr(request, "META", None)
    if not isinstance(meta, dict):
        return "unknown"
    x_forwarded_for = meta.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return meta.get("REMOTE_ADDR", "unknown")

# Signal handlers
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Log the login event
    UserLog.objects.create(
        user=user,
        username=user.username,
        event_type='login',
    ip_address=get_client_ip(request),
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # Log the logout event
    UserLog.objects.create(
        user=user,
        username=user.username,
        event_type='logout',
    ip_address=get_client_ip(request),
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    # Log the failed login attempt
    UserLog.objects.create(
        user=None,
        username=credentials.get('username', 'unknown'),
        event_type='login_failed',
        ip_address=get_client_ip(request),
    )

@receiver(pre_save, sender=User)
def log_password_change(sender, instance, **kwargs):
    # Check if the password has changed
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.password != instance.password:
                UserLog.objects.create(
                    user=instance,
                    username=instance.username,
                    event_type='password_change',
                    ip_address=None,  # Puede que no tengas el request acá
                    details="Password was changed.",
                )
        except User.DoesNotExist:
            pass