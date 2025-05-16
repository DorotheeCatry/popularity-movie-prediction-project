"""
URL configuration for django_cinema_interface project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings

handler400 = 'django.views.defaults.bad_request'
handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

urlpatterns = [
    # Redirect the root URL to the login page
    path('', RedirectView.as_view(url='user/login', permanent=False), name='root_redirect'),
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('user/', include('user.urls')),
    path('prediction/', include('movie_prediction.urls', namespace='movie_prediction'))
]