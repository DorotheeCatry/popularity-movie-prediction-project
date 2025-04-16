
# This is the URL configuration for the user app in a Django project.
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from .views import (
    CustomLoginView,
    ForcePasswordChangeView,
    ForgotPasswordView,
    ManagerListView,
    ManagerCreateView,
    ManagerUpdateView,
    ManagerDeleteView,
    HomeView
)

urlpatterns = [
    # Authentication URLs
    path('login', CustomLoginView.as_view(), name='login'),
    path('password-change/', ForcePasswordChangeView.as_view(), name='force_password_change'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    
    # Admin management of managers (only accessible by admin)
    path('managers/', ManagerListView.as_view(), name='manager_list'),
    path('managers/add/', ManagerCreateView.as_view(), name='manager_add'),
    path('managers/<int:pk>/edit/', ManagerUpdateView.as_view(), name='manager_edit'),
    path('managers/<int:pk>/delete/', ManagerDeleteView.as_view(), name='manager_delete'),
    # Home view after login
    path('home/', HomeView.as_view(), name='home'),
]
