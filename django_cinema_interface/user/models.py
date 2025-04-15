from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager

from typing import Optional

# User Management Models
class UserManager(BaseUserManager):
    """
    Custom User Manager to handle user creation and superuser creation.
    Automatically assigns roles:
        - 'admin' for superusers
        - 'manager' for all other users
    """
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'manager')  # Default role is client
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Superusers are advisors
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Adds role-based authentication and email as the primary identifier.
    """
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('admin', 'Administrateur'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)  # Email as unique identifier
    temp_password_reset_required = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep username for compatibility

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Assign role based on superuser status
        if self.is_superuser:
            self.role = 'admin'
        elif self.is_staff:
            self.role = 'manager'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"

