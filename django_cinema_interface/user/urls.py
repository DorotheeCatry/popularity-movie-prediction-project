from django.urls import path
from .views import (
    CustomLoginView,
    ForcePasswordChangeView,
    ForgotPasswordView,
    ManagerListView,
    ManagerCreateView,
    ManagerUpdateView,
    ManagerDeleteView,
)

urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-change/', ForcePasswordChangeView.as_view(), name='force_password_change'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    
    # Admin management of managers (only accessible by admin)
    path('managers/', ManagerListView.as_view(), name='manager_list'),
    path('managers/add/', ManagerCreateView.as_view(), name='manager_add'),
    path('managers/<int:pk>/edit/', ManagerUpdateView.as_view(), name='manager_edit'),
    path('managers/<int:pk>/delete/', ManagerDeleteView.as_view(), name='manager_delete'),
]
