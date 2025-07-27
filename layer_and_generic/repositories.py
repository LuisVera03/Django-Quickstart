from django.contrib.auth.models import User


# User
def get_user_by_username(username):
    return User.objects.filter(username=username).first()

def create_user(username, email, password):
    print("Creating user:", username)
    return User.objects.create_user(username=username, email=email, password=password)

