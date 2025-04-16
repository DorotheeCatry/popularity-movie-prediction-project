from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from .models import User
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomPasswordChangeForm

class CustomLoginView(LoginView):
    """
    Custom Login view.
    If the user logs in with a temporary password, they are redirected to force a password change.
    """
    template_name = 'user/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.temp_password_reset_required:
            return redirect('force_password_change')
        return response

class ForcePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Force the user to change their password if the password is temporary.
    Once the password is changed, update the user's temp_password_reset_required flag.
    """
    template_name = 'user/force_password_change.html'
    form_class = CustomPasswordChangeForm  # Use your custom or built-in form here.
    success_url = reverse_lazy('dashboard')  # Adjust the name to your dashboard URL.
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.temp_password_reset_required = False
        user.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Your password has been changed successfully.")
        return response

class ForgotPasswordView(PasswordResetView):
    """
    A view for handling forgotten password requests.
    """
    template_name = 'user/forgot_password.html'
    email_template_name = 'user/password_reset_email.html'
    subject_template_name = 'user/password_reset_subject.txt'
    success_url = reverse_lazy('login')


# Mixin to restrict access to admin-only views.
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        return redirect('dashboard')


# Admin management views for managers.
class ManagerListView(AdminRequiredMixin, ListView):
    """
    List all users with the role 'manager'.
    """
    model = User
    template_name = 'user/manager_list.html'
    context_object_name = 'managers'
    
    def get_queryset(self):
        return User.objects.filter(role='manager')


class ManagerCreateView(AdminRequiredMixin, CreateView):
    """
    Create a new manager. The created user will have a temporary password,
    which must be reset on first login.
    """
    model = User
    form_class = CustomUserCreationForm  # Form to create new users.
    template_name = 'user/manager_form.html'
    success_url = reverse_lazy('manager_list')
    
    def form_valid(self, form):
        # Mark that the password is temporary.
        form.instance.temp_password_reset_required = True
        return super().form_valid(form)


class ManagerUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update a manager's information.
    """
    model = User
    form_class = CustomUserUpdateForm  # Form to update user info.
    template_name = 'user/manager_form.html'
    success_url = reverse_lazy('manager_list')
    
    def get_queryset(self):
        return User.objects.filter(role='manager')


class ManagerDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete a manager account.
    """
    model = User
    template_name = 'user/manager_confirm_delete.html'
    success_url = reverse_lazy('manager_list')
    
    def get_queryset(self):
        return User.objects.filter(role='manager')
