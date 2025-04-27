from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .decorators import admin_required, can_manage_news
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

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@user_passes_test(is_admin)
def admin_panel(request):
    context = {
        'unapproved_users': CustomUser.objects.filter(is_approved=False),
        'all_users': CustomUser.objects.exclude(id=request.user.id),
        'recent_news': NewsPost.objects.order_by('-created_at')[:5]
    }
    return render(request, 'admin.html', context)

@user_passes_test(is_admin)
def approve_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_approved = True
        user.save()
        messages.success(request, f'Пользователь {user.username} подтверждён')
    return redirect('admin_panel')

@user_passes_test(is_admin)
def reject_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        username = user.username
        user.delete()
        messages.warning(request, f'Пользователь {username} отклонён и удалён')
    return redirect('admin_panel')

@user_passes_test(is_admin)
def assign_role(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=request.POST.get('user_id'))
        role = request.POST.get('role')
        
        if role == 'press_secretary':
            user.is_staff = True
            user.save()
            messages.success(request, f'{user.username} назначен пресс-секретарём')
        elif role == 'commander':
            # Логика для назначения командира
            messages.success(request, f'{user.username} назначен командиром')
        
    return redirect('admin_panel')


@user_passes_test(is_admin)
def delete_user(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_to_delete')
            if not user_id:
                messages.error(request, "Не выбран пользователь для удаления")
                return redirect('admin_panel')
            
            user = get_object_or_404(CustomUser, id=user_id)
            
            # Запрещаем удаление самого себя
            if user.id == request.user.id:
                messages.error(request, "Вы не можете удалить самого себя!")
                return redirect('admin_panel')
            
            username = user.username
            user.delete()
            messages.success(request, f'Пользователь {username} успешно удалён')
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
    
    return redirect('admin_panel')

@admin_required
def assign_role(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=request.POST.get('user_id'))
        role = request.POST.get('role')
        
        if role == 'press':
            user.role = CustomUser.PRESS_SECRETARY
            user.save()
            messages.success(request, f'{user.username} назначен пресс-секретарём.')
        elif role == 'commander':
            user.role = CustomUser.COMMANDER  
            user.is_staff = True
            user.save()
            messages.success(request, f'{user.username} назначен командиром.')
        else:
            messages.error(request, 'Недопустимая роль.')

    return redirect('admin_panel')

@can_manage_news
def add_news(request):
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, 'Новость успешно добавлена')
            return redirect('news_list')
    else:
        form = NewsPostForm()
    
    return render(request, 'news/add.html', {'form': form})

@can_manage_news
def edit_news(request, pk):
    news = get_object_or_404(NewsPost, pk=pk)
    if request.method == 'POST':
        form = NewsPostForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость успешно обновлена')
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsPostForm(instance=news)
    
    return render(request, 'news/edit_news.html', {'form': form, 'news': news})
@can_manage_news
def delete_news(request, news_id):
    if request.method == 'POST':
        news = get_object_or_404(NewsPost, id=news_id)
        news.delete()
        messages.warning(request, 'Новость удалена')
    return redirect('admin_panel')