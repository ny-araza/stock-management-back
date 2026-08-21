from django.contrib.auth.base_user import BaseUserManager


class TUsersManager(BaseUserManager):
    def create_user(self, use_login, password=None, **extra_fields):
        if not use_login:
            raise ValueError("Le login est obligatoire")

        user = self.model(use_login=use_login, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, use_login, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(use_login, password, **extra_fields)
