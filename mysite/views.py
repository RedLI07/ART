from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RegisterForm
from .models import CustomUser

def index(request):
    return render(request, 'index.html')


def school(request):
    return render(request, 'school.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Аккаунт создается с is_approved=False
            return redirect('wait_for_approval')  # Перенаправляем на страницу ожидания
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    if not request.user.is_approved:
        messages.warning(request, 'Ваш аккаунт ожидает одобрения администратора.')
        return redirect('index')
    return render(request, 'profile.html', {'user': request.user})

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