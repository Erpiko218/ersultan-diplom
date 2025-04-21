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


class UserSettingsForm(forms.ModelForm):
	class Meta:
		model = UserModel
		fields = (
			"avatar",
			"first_name",
			"last_name",
			"email",
			"phone",
			"address",
			"date_of_birth",
			"groups",
		)
		widgets = {
			"date_of_birth": forms.DateInput(attrs={"type": "date", "class": "input input-bordered"}),
			"groups": forms.SelectMultiple(attrs={"class": "select select-bordered"}),
			"first_name": forms.TextInput(attrs={"class": "input input-bordered"}),
			"last_name": forms.TextInput(attrs={"class": "input input-bordered"}),
			"email": forms.EmailInput(attrs={"class": "input input-bordered"}),
			"phone": forms.TextInput(attrs={"class": "input input-bordered"}),
			"address": forms.Textarea(attrs={"class": "textarea textarea-bordered", "rows": 3}),
		}
		labels = {
			"avatar": "Аватар",
			"first_name": "Имя",
			"last_name": "Фамилия",
			"email": "Email",
			"phone": "Телефон",
			"address": "Адрес",
			"date_of_birth": "Дата рождения",
			"groups": "Роли",
		}
