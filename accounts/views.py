from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.forms import AccountsUserCreationForm


class RegisterView(CreateView):
    form_class = AccountsUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')  # После регистрации переходим на главную

    def form_valid(self, form):
        # Сохраняем нового пользователя
        response = super().form_valid(form)
        # Автоматически логиним пользователя
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')
