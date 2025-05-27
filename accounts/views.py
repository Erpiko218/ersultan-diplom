from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.forms import AccountsUserCreationForm, EmailAuthenticationForm, UserSettingsForm
from rental.models import Rental, Transaction


class RegisterView(CreateView):
	form_class = AccountsUserCreationForm
	template_name = 'accounts/register.html'
	success_url = reverse_lazy('home')  # После регистрации переходим на главную

	def form_valid(self, form):
		# Сохраняем нового пользователя
		response = super().form_valid(form)
		user = authenticate(
			self.request,
			username=self.object.username,
			password=form.cleaned_data['password1']  # пароль из формы
		)
		# Если успешно — логиним
		if user is not None:
			login(self.request, user)
		return response


class CustomLoginView(LoginView):
	form_class = EmailAuthenticationForm
	template_name = 'accounts/login.html'
	redirect_authenticated_user = True

	def get_success_url(self):
		return reverse_lazy('home')


def custom_logout_view(request):
	logout(request)
	return redirect('home')  # 'home' — это name из urls.py, например: path('', views.home, name='home')


@login_required
def notifications_update(request):
	if request.method == "POST":
		user = request.user
		# checkbox в POST будет присутствовать только если checked
		user.email_news = 'email_news' in request.POST
		user.sms_alerts = 'sms_alerts' in request.POST
		user.push_notifications = 'push_notifications' in request.POST
		user.save()
		messages.success(request, "Настройки уведомлений сохранены.")
	return redirect("settings")


@login_required
def settings_view(request):
	user = request.user
	if request.method == "POST":
		form = UserSettingsForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()
			messages.success(request, "Настройки успешно сохранены.")
			return redirect("settings")
	else:
		form = UserSettingsForm(instance=user)

	return render(request, "settings.html", {
		"form": form,
		"balance": user.balance,
	})


@login_required
def dashboard(request):
	user = request.user
	balance = user.balance

	transactions = (
		Transaction.objects
		.filter(user=user)
		.order_by("-timestamp")[:10]
	)

	current_rentals = (
		Rental.objects
		.filter(user=user, status="OWNED")
		.select_related("car")[:10]
	)

	history_rentals = (
		Rental.objects
		.filter(user=user, status__in=["COMPLETED", "REJECTED"])
		.select_related("car")
		.order_by("-end_time")[:10]
	)

	return render(request, "accounts/dashboard.html", {
		"balance": balance,
		"transactions": transactions,
		"current_rentals": current_rentals,
		"history_rentals": history_rentals,
	})


@login_required
def profile(request):
	return render(request, "profile.html")


@login_required
def wallet(request):
	balance = request.user.balance
	txs = Transaction.objects.filter(user=request.user).order_by("-timestamp")[:20]
	return render(request, "wallet.html", {
		"balance": balance,
		"transactions": txs,
	})
