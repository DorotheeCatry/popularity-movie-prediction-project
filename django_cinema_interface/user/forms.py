from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new manager account.
    The admin provides a temporary password which the user must change upon first login.
    """
    class Meta:
        model = User
        # Include the fields you'd like the admin to fill when creating a user.
        fields = ('email', 'username', 'first_name', 'last_name')
        # Note: Password fields (password1 and password2) are provided by UserCreationForm.

class CustomUserUpdateForm(UserChangeForm):
    """
    Form for updating an existing manager's account details.
    Excludes the password field to prevent accidental changes.
    """
    password = None  # Exclude the password field

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom form for changing the user's password.
    Inherits from Django's built-in PasswordChangeForm,
    which manages the old password and verifies the new password entries.
    """
    class Meta:
        model = User
        # Although PasswordChangeForm already defines its own fields,
        # the Meta class is provided here for completeness.
        fields = ('old_password', 'new_password1', 'new_password2')
