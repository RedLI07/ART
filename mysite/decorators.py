from django.core.exceptions import PermissionDenied
from .models import CustomUser

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_superuser or request.user.role == CustomUser.COMMANDER):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def can_manage_news(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.can_manage_news():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper