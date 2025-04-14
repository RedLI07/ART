from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, first_name='', last_name='', **extra_fields):
        if not username:
            raise ValueError("Пользователь должен иметь username")
        
        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)  # Суперпользователь одобрен автоматически

        return self.create_user(username, password=password, **extra_fields)

class CustomUser(AbstractUser):
    # Основные поля
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Логин",
        help_text="Обязательное поле. Не более 150 символов."
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name="Имя",
        blank=True
    )
    last_name = models.CharField(
        max_length=30,
        verbose_name="Фамилия",
        blank=True
    )
    
    # Статус одобрения
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Аккаунт одобрен",
        help_text="Разрешить пользователю вход в систему."
    )

    # Настройки аутентификации
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Поля не требуются при createsuperuser

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ("can_approve_user", "Может одобрять пользователей"),
        ]

    def __str__(self):
        return self.username