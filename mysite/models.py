from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from PIL import Image
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
from django.utils.text import slugify
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Пользователь должен иметь username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', CustomUser.COMMANDER)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
    PRESS_SECRETARY = 'press'
    COMMANDER = 'commander'
    ROLE_CHOICES = [
        (PRESS_SECRETARY, 'Пресс-секретарь'),
        (COMMANDER, 'Командир'),
    ]
    
    username = models.CharField(max_length=150, unique=True, verbose_name="Логин")
    join_year = models.PositiveIntegerField(
        verbose_name="Год вступления",
        null=True,
        blank=True,
        validators=[MinValueValidator(2000)]
    )
    bricks_count = models.PositiveIntegerField(
        verbose_name="Количество кирпичей",
        default=0
    )
    about = models.TextField(verbose_name="О себе", blank=True, null=True)
    achievements = models.TextField(verbose_name="Достижения", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Роль"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def is_profile_complete(self):
        return all([
            self.join_year is not None,
            self.about not in [None, ''],
            self.achievements not in [None, '']
        ])

    def get_bricks_display(self):
        return "Кандидат" if self.bricks_count == 0 else f"{self.bricks_count} кирпича"
    
    def can_manage_news(self):
        return self.role in [self.COMMANDER, self.PRESS_SECRETARY] or self.is_superuser

class UserPhoto(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='user_photos/')
    is_avatar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_avatar', '-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            img_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            with Image.open(img_path) as img:
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(img_path)
                    
                # Создание миниатюры
                thumbnail_size = (200, 200)
                img.thumbnail(thumbnail_size)
                thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', self.image.name)
                os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
                img.save(thumbnail_path)


class NewsPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-адрес")  # Добавляем это поле
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='news_images/', verbose_name="Изображение")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']