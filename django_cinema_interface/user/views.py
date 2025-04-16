from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from .models import User
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomPasswordChangeForm

class CustomLoginView(LoginView):
    template_name = 'user/login.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request based on user authentication status.

        If the user is already authenticated, redirect them to the home page.
        Otherwise, proceed with the default dispatch behavior.
        """
        # If user is already authenticated, send them to home.
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle a valid login form submission.

        If the user is a manager with a temporary password, redirect them to change it.
        Otherwise, redirect to the home page.
        """
        # Log in the user normally.
        response = super().form_valid(form)
        user = self.request.user
        # Only for managers with a temporary password, force password change.
        if user.role == 'manager' and user.temp_password_reset_required:
            return redirect('force_password_change')
        # Otherwise, send the user to home.
        return redirect('home')


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


class HomeView(TemplateView):
    """
    A simple home view that acts as the landing page after login.
    More details and features will be implemented later.
    """
    template_name = "user/home.html"