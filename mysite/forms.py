from django import forms
from .models import CustomUser, UserPhoto
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, NewsPost

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=False, label="Имя")
    last_name = forms.CharField(required=False, label="Фамилия")
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name')

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
