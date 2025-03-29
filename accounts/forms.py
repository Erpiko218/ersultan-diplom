from django.contrib.auth.forms import UserCreationForm
from django import forms

from accounts.models import UserModel


class AccountsUserCreationForm(UserCreationForm):
	email = forms.EmailField(required=True, label="Электронная почта")
	phone = forms.CharField(required=True, label="Телефон")

	class Meta:
		model = UserModel
		fields = ("username", "first_name", "last_name", "email", "phone")
