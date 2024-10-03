# backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .utils import consistent_encrypt

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            # Hash the email to compare
            encrypted_email = consistent_encrypt(email)
            user = UserModel.objects.get(email_hash=encrypted_email)

            # Check the password against the stored hash
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
