from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone', 'role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Infos supplémentaires', {'fields': ('role', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)