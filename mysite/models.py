from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator

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
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def is_profile_complete(self):
        return all([
            self.join_year is not None,
            self.about not in [None, ''],
            self.achievements not in [None, '']
        ])

    def get_bricks_display(self):
        return "Кандидат" if self.bricks_count == 0 else f"{self.bricks_count} кирпича"

class UserPhoto(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='user_photos/')
    is_avatar = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_avatar', '-created_at']