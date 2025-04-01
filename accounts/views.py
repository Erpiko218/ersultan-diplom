from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.forms import AccountsUserCreationForm, EmailAuthenticationForm


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
