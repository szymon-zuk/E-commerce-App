from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import UserRole


class CustomUserAccountAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = UserRole
    list_display = [
        "username",
        "role",
        "email",
        "is_staff",
    ]
    list_filter = ["username", "role"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)


admin.site.register(UserRole, CustomUserAccountAdmin)
