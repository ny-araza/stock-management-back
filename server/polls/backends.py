import hashlib
from django.contrib.auth.backends import BaseBackend
from .models import TUsers


class TUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print("jgfkldgjdflgldfgfjdlg")
        try:
            user = TUsers.objects.get(use_login=username)
            hashed_password = hashlib.sha256(
                password.encode('utf-8')).hexdigest()
            print("hashed => ",hashed_password)
            if user.use_pwd == hashed_password:
                return user
        except TUsers.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return TUsers.objects.get(pk=user_id)
        except TUsers.DoesNotExist:
            return None
