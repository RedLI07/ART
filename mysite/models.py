from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Пользователь должен иметь username")
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)  # Автоматически одобряем суперпользователя

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(username, password=password, **extra_fields)

class CustomUser(AbstractUser):
    # username остаётся (используется для входа)
    email = models.EmailField(unique=True, verbose_name="Email", blank=True, null=True)  # Необязательное поле
    first_name = models.CharField(max_length=30, verbose_name="Имя", blank=True)
    last_name = models.CharField(max_length=30, verbose_name="Фамилия", blank=True)
    is_approved = models.BooleanField(default=False, verbose_name="Аккаунт одобрен")

    USERNAME_FIELD = 'username'  # Теперь вход по username
    REQUIRED_FIELDS = []  # При createsuperuser не запрашивает дополнительные поля

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def send_approval_email(self):
        if self.email:
            subject = 'Ваш аккаунт одобрен!'
            message = f'Уважаемый(ая) {self.get_full_name()}! Ваш аккаунт был одобрен администратором.'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'