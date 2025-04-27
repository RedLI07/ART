from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NewsPost

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_staff', 'is_superuser', 'is_approved')
    list_filter = ('role', 'is_staff', 'is_superuser')
    list_editable = ('is_approved',)
    actions = ['make_press_secretary', 'make_commander']

    def make_press_secretary(self, request, queryset):
        queryset.update(role=CustomUser.PRESS_SECRETARY, is_staff=True)
    make_press_secretary.short_description = "Назначить пресс-секретарями"

    def make_commander(self, request, queryset):
        queryset.update(role=CustomUser.COMMANDER, is_staff=True, is_superuser=True)
    make_commander.short_description = "Назначить командирами"

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