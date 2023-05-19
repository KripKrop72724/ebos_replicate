from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from ebos2201.models.m01_core_mas import User


class UsernameOrEmailAuthBackend(ModelBackend):
    """
    Custom authentication backend to login users using username or email address.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
            if user.check_password(password):
                return user
            return
        except User.DoesNotExist:
            return

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
