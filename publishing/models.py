from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_paid = models.BooleanField(default=False)
    author = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'
    groups = models.ManyToManyField(Group, related_name='publishing_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='publishing_user_permissions')

    def __str__(self):
        return self.phone_number
