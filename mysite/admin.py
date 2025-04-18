from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NewsPost

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_approved')
    list_editable = ('is_approved',)  # Разрешить редактирование галочки в списке
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Одобрить выбранных пользователей"

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'created_at', 'is_published')  # Добавили slug
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}  # Теперь это будет работать
    date_hierarchy = 'created_at'
    fields = ('title', 'slug', 'content', 'image', 'is_published')  # Добавили slug

    def save_model(self, request, obj, form, change):
        if not obj.author_id:  # Если автор не указан
            obj.author = request.user  # Устанавливаем текущего пользователя
        super().save_model(request, obj, form, change)