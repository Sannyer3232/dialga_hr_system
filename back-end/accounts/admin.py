from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Mostra o campo 'role' quando você for EDITAR um usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Informações do Cargo', {'fields': ('role',)}),
    )
    # Mostra o campo 'role' quando você for CRIAR um novo usuário pelo Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações do Cargo', {'fields': ('role',)}),
    )
    
    # Quais colunas mostrar na lista geral de usuários
    list_display = ('username', 'email', 'role', 'is_staff')

admin.site.register(User, CustomUserAdmin)