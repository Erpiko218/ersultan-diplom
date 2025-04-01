from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from accounts.models import UserModel


class AccountsUserCreationForm(UserCreationForm):
	email = forms.EmailField(required=True, label="Электронная почта")
	phone = forms.CharField(required=True, label="Телефон")

	class Meta:
		model = UserModel
		fields = ("username", "first_name", "last_name", "email", "phone")


class EmailAuthenticationForm(forms.Form):
	email = forms.EmailField(label="Электронная почта")
	password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop("request", None)
		super().__init__(*args, **kwargs)
		self.user_cache = None

	def clean(self):
		email = self.cleaned_data.get("email")
		password = self.cleaned_data.get("password")

		if email and password:
			try:
				username = UserModel.objects.get(email=email).username
			except UserModel.DoesNotExist:
				raise forms.ValidationError("Пользователь с такой почтой не найден.")
			self.user_cache = authenticate(self.request, username=username, password=password)
			if self.user_cache is None:
				raise forms.ValidationError("Неверная почта или пароль.")
		return self.cleaned_data

	def get_user(self):
		return self.user_cache
