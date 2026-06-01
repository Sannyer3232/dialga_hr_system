from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('O usuário precisa ter um username.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Vamos garantir que um superuser sempre seja criado como ADMIN
        extra_fields.setdefault('role', 'ADMIN') 

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
    
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'HR AdmAdministrator'),
        ('MANAGER', 'Manager'),
        ('RPA_BOT', 'Automation Robot')
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ADMIN')