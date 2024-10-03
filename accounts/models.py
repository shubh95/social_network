from accounts.utils import consistent_encrypt

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.search import TrigramSimilarity

from django.db import models

from encrypted_model_fields.fields import EncryptedEmailField, EncryptedCharField



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        # Consistently encrypt email
        encrypted_email = consistent_encrypt(email)
        user = self.model(
            email_hash=encrypted_email,
            email=email,
            **extra_fields
        )

        user.set_password(password)  # Set the user's password securely
        user.save(using=self._db)     # Save the user instance
        return user

    def get_by_natural_key(self, email):
        # Allows querying by natural email
        encrypted_email = consistent_encrypt(email)
        return self.get(email_hash=encrypted_email)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('role') != 'admin':
            raise ValueError("Superuser must have role='admin'.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUserQuerySet(models.QuerySet):
    
    def search(self, q):
        encrypted_query = consistent_encrypt(q)
        
        # include the user if its email matches the query
        queryset = self.filter(
            models.Q(email_hash=encrypted_query)
        )

        if queryset.exists():
            return queryset
        
        # If the search keyword contains any part of the name, return a list of all matching users.
        # Implement full-text search using PostgreSQL for name-based queries to enhance performance and accuracy.
        queryset = self.annotate(
            first_name_similarity=TrigramSimilarity('first_name', q)
        ).annotate(
            last_name_similarity=TrigramSimilarity('last_name', q)
        ).filter(
            models.Q(first_name_similarity__gt=0.1) | models.Q(last_name_similarity__gt=0.1)
        ).order_by('-first_name_similarity', '-last_name_similarity')

        return queryset
    
    def search_by_email(self, email):
        encrypted_email = consistent_encrypt(email)
        return self.filter(email_hash=encrypted_email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email_hash = models.CharField(max_length=64, unique=True)
    email = EncryptedEmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, default="write", choices=[("read", "read"), ("write", "write"), ("admin", "admin")])
    
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager.from_queryset(CustomUserQuerySet)()

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.role == "admin"


class BlockedUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="blocked_users")
    blocked_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.blocked_user}"
    
    class Meta:
        unique_together = ('user', 'blocked_user')
        verbose_name_plural = "Blocked Users"
        verbose_name = "Blocked User"
        ordering = ['created_at']
