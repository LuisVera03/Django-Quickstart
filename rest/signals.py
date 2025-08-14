from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.models import User
from .models import UserLog
from django.utils.timezone import now

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserLog.objects.create(
        user=user,
        username=user.username,
        event_type='login',
        ip_address=get_client_ip(request),
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserLog.objects.create(
        user=user,
        username=user.username,
        event_type='logout',
        ip_address=get_client_ip(request),
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    UserLog.objects.create(
        user=None,
        username=credentials.get('username', 'unknown'),
        event_type='login_failed',
        ip_address=get_client_ip(request),
    )

@receiver(pre_save, sender=User)
def log_password_change(sender, instance, **kwargs):
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