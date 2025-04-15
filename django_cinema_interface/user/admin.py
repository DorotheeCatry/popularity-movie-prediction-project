# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'is_staff', 'is_superuser')
    
    def has_add_permission(self, request):
        # Only allow adding if the current user is an admin
        return request.user.role == 'admin'

admin.site.register(User, UserAdmin)
