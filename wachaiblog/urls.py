from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from users.views import manual_logout
from users.views import phone_password_reset, phone_reset_confirm

urlpatterns = [
    path('admin/', admin.site.urls),

    # User Authentication URLs
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', manual_logout, name='logout'),
    path('', include('wachai.urls')),
    path('reset-password-phone/', phone_password_reset,
         name="phone_password_reset"),
    path('reset-password-phone/confirm/',
         phone_reset_confirm, name="phone_reset_confirm"),
    path('chat/', include('chat.urls', namespace='chat')),

]

# Serve media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
