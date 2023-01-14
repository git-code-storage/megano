import logging
from django.contrib.auth import views
from django.shortcuts import render, redirect
from datetime import datetime
from shop.utils import get_total_cart_items
from .utils import add_cart_to_user, registration_base

# Create your views here.
logger = logging.getLogger(__name__)


class LoginView(views.LoginView):

    template_name = 'user/login.html'

    def get_success_url(self):
        logger.info(f'[LoginView.get_success_url] - {datetime.now()} - Login completed: {self.request.user}')
        return self.get_redirect_url() or self.get_default_redirect_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_cart_items, total_cost = get_total_cart_items(self.request)
        context['total_cart_items'] = total_cart_items
        context['total_cost'] = total_cost
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get('username')
            add_cart_to_user(request, email, 'LoginView.post')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class LogoutView(views.LogoutView):

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'[LogoutView.get_success_url] - {datetime.now()} - Logout completed: {self.request.user}')
        return super().dispatch(request, *args, **kwargs)


def registration(request):
    check_succsess, context = registration_base(request, 'user:registration')
    if check_succsess:
        return redirect('/')
    return render(request, 'user/register.html', context)


def profile(request):
    pass
