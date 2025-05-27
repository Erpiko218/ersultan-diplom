from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin

from accounts.models import UserModel


class UserForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = '__all__'


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    form = UserForm
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']
    readonly_fields = ['last_login', 'date_joined']