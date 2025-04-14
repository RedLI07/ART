from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('school/', views.school, name='school'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/complete/', views.complete_profile, name='complete_profile'),
    path('wait_for_approval/', views.wait_for_approval, name='wait_for_approval'),
    
    # Простые URL для входа/выхода
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        extra_context={'title': 'Вход в систему'}
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='logout.html',
        extra_context={'title': 'Выход из системы'}
    ), name='logout'),
    
    # Только один админский URL
    path('admin/approve-users/', views.approve_users, name='approve_users'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)