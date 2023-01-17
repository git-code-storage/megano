import logging
from shop.models import Product, Order, OrderItem
from .models import CustomUser
from datetime import datetime
from shop.utils import get_total_cart_items
from .forms import RegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import login

logger = logging.getLogger(__name__)


def add_cart_to_user(request, email, view):

    logger.info(f'[{view}] - {datetime.now()} - Entered email: {email}')
    customer = CustomUser.objects.get(email=email)
    logger.info(f'[{view}] - {datetime.now()} - User: {customer.email}')
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    logger.info(f'[{view}] - {datetime.now()} - Order: {order.id}')
    order.save()
    if 'cart' in request.session:
        for item in request.session['cart'].keys():
            product = Product.objects.get(slug=item)
            logger.info(f'[{view}] - {datetime.now()} - Product: {product.name}')
            orderitem, created = OrderItem.objects.get_or_create(product=product, order=order)
            logger.info(f'[{view}] - {datetime.now()} - Orderitem: {orderitem.id}, '
                        f'quantity: {orderitem.quantity}')
            orderitem.quantity += request.session['cart'][item]
            logger.info(f'[{view}] - {datetime.now()} - Quantity after summ: {orderitem.quantity}')
            orderitem.save()


def registration_base(request, view):

    errors = None
    check_succsess = False
    total_cart_items, total_cost, order = get_total_cart_items(request)

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            add_cart_to_user(request, user.email, view)
            login(request, user)
            check_succsess = True
        else:
            errors = form.errors
            logger.info(f'[{view}] - {datetime.now()} - Errors: {errors}')
    else:
        form = RegisterForm(request.GET)

    context = {'errors': errors,
               'total_cart_items': total_cart_items,
               'total_cost': total_cost,
               'form': form,
               }

    return check_succsess, context

