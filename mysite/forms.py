from django import forms
from .models import CustomUser, UserPhoto
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, NewsPost
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=False, label="Имя")
    last_name = forms.CharField(required=False, label="Фамилия")
    vk_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://vk.com/yourprofile'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'vk_link')

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data and initial:
            return initial
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return super().clean(data, initial)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['join_year', 'bricks_count', 'about', 'achievements']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
            'achievements': forms.Textarea(attrs={'rows': 4}),
        }

    join_year = forms.IntegerField(label="Год вступления",
    min_value=2006, 
    required=False, 
    widget=forms.NumberInput(attrs={'placeholder': 'Введите год вступления'})
)
    
class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_approved:
            raise forms.ValidationError(
                _("Ваш аккаунт ожидает подтверждения администратора."),
                code='not_approved',
            )

class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserPhoto
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'})
        }

class MultiplePhotosForm(forms.Form):
    photos = MultipleFileField(
        label='Дополнительные фотографии',
        required=False,
        widget=MultipleFileInput(attrs={'accept': 'image/*'})
    )


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ('title', 'content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class AvatarForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Загрузить новый аватар")

    class Meta:
        model = UserPhoto
        fields = ['image']

class AssignRoleForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_approved=True),
        label="Пользователь"
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        label="Роль"
    )