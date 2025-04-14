from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_approved')
    list_editable = ('is_approved',)  # Разрешить редактирование галочки в списке
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Одобрить выбранных пользователей"

admin.site.register(CustomUser, CustomUserAdmin)