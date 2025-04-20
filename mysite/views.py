from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import *
from .models import *

def index(request):
    return render(request, 'index.html')


def school(request):
    return render(request, 'school.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Требуется одобрение админа
            user.save()
            return redirect('wait_for_approval')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def complete_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        avatar_form = AvatarForm(request.POST, request.FILES)
        photos_form = MultiplePhotosForm(request.POST, request.FILES)

        if profile_form.is_valid():
            profile_form.save()

            if avatar_form.is_valid() and 'image' in request.FILES:
                UserPhoto.objects.filter(user=request.user, is_avatar=True).delete()
                avatar = avatar_form.save(commit=False)
                avatar.user = request.user
                avatar.is_avatar = True
                avatar.save()

            if photos_form.is_valid() and 'photos' in request.FILES:
                for file in request.FILES.getlist('photos'):
                    UserPhoto.objects.create(user=request.user, image=file)

            return redirect('profile')

    else:
        profile_form = ProfileForm(instance=request.user)
        avatar_form = AvatarForm()
        photos_form = MultiplePhotosForm()

    return render(request, 'complete_profile.html', {
        'profile_form': profile_form,
        'avatar_form': avatar_form,
        'photos_form': photos_form
    })

@login_required
def profile(request, username=None):
    User = get_user_model()
    if username is None:
        user_profile = request.user

        if not user_profile.is_profile_complete():
            return redirect('complete_profile')
        
    else:
        user_profile = get_object_or_404(User, username=username)
    
    avatar = user_profile.photos.filter(is_avatar=True).first()
    photos = user_profile.photos.filter(is_avatar=False)
    
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'avatar': avatar,
        'photos': photos,
        
    })

# Админ-панель для одобрения
@user_passes_test(lambda u: u.is_superuser)
def approve_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        user = CustomUser.objects.get(id=user_id)
        if action == 'approve':
            user.is_approved = True
            user.save()
            user.send_approval_email()
            messages.success(request, f'Пользователь {user.get_full_name()} одобрен!')
    
    unapproved = CustomUser.objects.filter(is_approved=False)
    return render(request, 'admin/approve_users.html', {'users': unapproved})


def wait_for_approval(request):
    return render(request, 'wait_for_approval.html')


def news_list(request):
    news = NewsPost.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'news/list.html', {'news': news})

def news_detail(request, pk):
    post = get_object_or_404(NewsPost, pk=pk, is_published=True)
    return render(request, 'news/detail.html', {'post': post})

@user_passes_test(lambda u: u.is_staff)
def add_news(request):
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('news_list')
    else:
        form = NewsPostForm()
    return render(request, 'news/add.html', {'form': form})

@login_required
def change_profile(request):
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user)
        avatar_form = AvatarForm(request.POST, request.FILES)
        photos_form = MultiplePhotosForm(request.POST, request.FILES)

        if profile_form.is_valid():
            profile_form.save()

            # Обработка аватара
            if avatar_form.is_valid() and 'image' in request.FILES:
                # Удалить старый аватар
                UserPhoto.objects.filter(user=user, is_avatar=True).delete()
                
                avatar = avatar_form.save(commit=False)
                avatar.user = user
                avatar.is_avatar = True
                avatar.save()

            # Обработка дополнительных фото
            if photos_form.is_valid() and 'photos' in request.FILES:
                for file in request.FILES.getlist('photos'):
                    UserPhoto.objects.create(user=user, image=file)

            return redirect('profile')

    else:
        profile_form = ProfileForm(instance=user)
        avatar_form = AvatarForm()
        photos_form = MultiplePhotosForm()

    # Получение текущего аватара и фото
    avatar = UserPhoto.objects.filter(user=user, is_avatar=True).first()
    user_photos = UserPhoto.objects.filter(user=user, is_avatar=False)

    return render(request, 'change_profile.html', {
        'profile_form': profile_form,
        'avatar_form': avatar_form,
        'photos_form': photos_form,
        'avatar': avatar,
        'user_photos': user_photos,
    })

def user_list(request):
    users = CustomUser.objects.all().order_by('-bricks_count')

    user_data = []
    for user in users:
        avatar = user.photos.filter(is_avatar=True).first()
        user_data.append({
            'user': user,
            'avatar': avatar,
            'bricks': user.get_bricks_display(),
        })

    context = {
        'title': 'Список участников',
        'users': user_data
    }

    return render(request, 'participants.html', context)
