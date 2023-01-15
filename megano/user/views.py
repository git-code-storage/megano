import logging
from django.contrib.auth import views, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import Prefetch
from datetime import datetime
from shop.utils import get_total_cart_items
from .utils import add_cart_to_user, registration_base
from django.contrib import messages
from .forms import ChangeForm, PassChangeForm
from .models import CustomUser, DeliveryAddress
from shop.models import Order, OrderItem, Product, Delivery, Payment, TypeOfDelivery
from django.contrib.auth.decorators import login_required

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


@login_required
def profile(request):

    total_cart_items, total_cost = get_total_cart_items(request)
    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost

    if request.method == 'POST':
        form = ChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = CustomUser.objects.get(email=request.user.email)
            user.phone = form.cleaned_data.get('phone')
            logger.info(f'[form.cleaned_data.get(phone)]: {form.cleaned_data.get("phone")}')
            user.avatar = form.cleaned_data.get('avatar')
            user.name = form.cleaned_data.get('name')
            logger.info(f'[form.cleaned_data.get(name)]: {form.cleaned_data.get("name")}')
            user.save()

            messages.success(request, 'Your personal data was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, '<font color="##ff0000">Please correct the error below.</font>')

    return render(request, 'user/profile.html', context)


@login_required
def change_password(request):

    total_cart_items, total_cost = get_total_cart_items(request)
    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost

    if request.method == 'POST':
        form = PassChangeForm(user=request.user, data=request.POST)
        try:
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('change_password')
        except (ValidationError, KeyError):
            messages.error(request, '<font color="##ff0000">The password has not been changed! </br>'
                                    'The new password field and the repeat field are mismatched!</font>')
            form = PassChangeForm(user=request.user)
    else:
        form = PassChangeForm(user=request.user)
    context['form'] = form

    return render(request, 'user/change_password.html', context)


@login_required
def account(request):
    pr1 = Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product').all())
    orders = Order.objects.prefetch_related(pr1, 'delivery', 'payment')\
        .filter(customer__email=request.user.email)
    total_cart_items, total_cost = get_total_cart_items(request)
    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['orders'] = orders

    return render(request, 'user/account.html', context)


@login_required
def history_order(request):
    total_cart_items, total_cost = get_total_cart_items(request)
    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost

    return render(request, 'user/history_order.html', context)
