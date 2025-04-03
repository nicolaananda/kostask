from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_admin')
    list_filter = ('is_staff', 'is_superuser', 'is_admin')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'is_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'is_admin')}),
    )
