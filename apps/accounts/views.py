from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('pos:dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
