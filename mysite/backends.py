from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class ApprovedUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_approved