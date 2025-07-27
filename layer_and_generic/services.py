from django.contrib.auth import authenticate, login, logout

# Import functions for data manipulation by users
from .repositories import create_user, get_user_by_username

#
## Login / Register
#

# Attempts to authenticate and log in a user. Returns True if successful, otherwise False.
def try_login(request, username, password):
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return True
    return False

# Registers a new user if the username is not already taken. Returns the created user or None if the username already exists.
def register_user(username, email, password, password_confirm):
    if get_user_by_username(username):
        return None
    return create_user(username, email, password)

#Log out
def perform_logout(request):
    logout(request)

