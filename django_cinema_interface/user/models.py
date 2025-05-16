from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from typing import Optional

class UserManager(BaseUserManager):
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'manager')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('admin', 'Administrateur'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='manager')
    email = models.EmailField(unique=True)
    temp_password_reset_required = models.BooleanField(default=True)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        elif self.is_staff:
            self.role = 'manager'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"