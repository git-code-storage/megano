import logging
from django.urls import reverse
from django.shortcuts import render, redirect
from shop.utils import get_total_cart_items
from shop.models import Product, Order, OrderItem, Delivery, TypeOfDelivery, Payment
from user.models import DeliveryAddress
from .forms import DeliveryForm, ChoicePaymentForm, CardForm
from user.utils import registration_base
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic


logger = logging.getLogger(__name__)
#logger.info(f'cart.views')


def order_step_one(request):

    check_succsess, context = registration_base(request, 'oder_one_step')
    if check_succsess:
        return redirect(reverse('oder_one_step'))
    return render(request, 'cart/order_one.html', context)


@login_required
def order_step_two(request):

    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            with atomic():
                delivery = form.cleaned_data.get('delivery')
                address = form.cleaned_data.get('address')
                city = form.cleaned_data.get('city')
                address, created = DeliveryAddress.objects.get_or_create(user=request.user, address=address, city=city)
                address.save()
                type_of_delivery = TypeOfDelivery.objects.get(type_of_delivery=delivery)
                delivery, created = Delivery.objects.get_or_create(order=order, complete=False)
                delivery.type_of_delivery = type_of_delivery
                delivery.address = address
                delivery.save()
            return redirect(reverse('order_step_three'))
        else:
            context['form'] = form
            return render(request, 'cart/order_two.html', context)
    else:
        form = DeliveryForm()
        delivery, created = Delivery.objects.get_or_create(order=order, complete=False)
        if not created:
            if delivery.address:
                context['address'] = delivery.address.address
                context['city'] = delivery.address.city
                context['type_of_delivery'] = delivery.type_of_delivery.type_of_delivery
            else:
                context['address'] = None
                context['city'] = None
                context['type_of_delivery'] = None
        context['form'] = form
    return render(request, 'cart/order_two.html', context)


@login_required
def order_step_three(request):
    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    if request.method == 'POST':
        form = ChoicePaymentForm(request.POST)
        if form.is_valid():
            with atomic():
                payment_way = form.cleaned_data.get('payment_way')
                order = Order.objects.get(customer=request.user, complete=False)

                payment, created = Payment.objects.get_or_create(order=order,
                                                                 complete=False)
                payment.payment_way = payment_way
                payment.save()
                return redirect(reverse('order_step_four'))
        else:
            context['form'] = form
            return render(request, 'cart/order_two.html', context)
    else:
        form = ChoicePaymentForm()
        payment, created = Payment.objects.get_or_create(order=order, complete=False)
        context['payment_way'] = payment.payment_way
        context['form'] = form
    return render(request, 'cart/order_three.html', context)


@login_required
def order_step_four(request):
    total_cart_items, total_cost, order = get_total_cart_items(request)
    in_cart = OrderItem.objects.select_related('product').filter(order=order)

    delivery = order.delivery
    payment = order.payment
    delivery_address = DeliveryAddress.objects.filter(user=request.user).last()

    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['in_cart'] = in_cart
    context['total'] = total_cost
    context['delivery'] = delivery
    context['payment'] = payment
    context['delivery_address'] = delivery_address

    return render(request, 'cart/order_four.html', context)


@login_required
def payment(request):

    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    payment = order.payment

    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['payment'] = None

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            try:
                card = form.cleaned_data.get('card')
                card = card[:4] + card[5:]
                card = int(card)
            except:
                payment.error_status = True
                payment.error_msg = 'error converting the card number to an integer'
                payment.save()
                context['payment'] = payment
                if payment.payment_way == 'ACNT':
                    return render(request, 'cart/paymentsomeone.html', context)
                return render(request, 'cart/payment.html', context)
            if (len(str(card)) == 8) and (card % 2 == 0):
                with atomic():
                    orderitems = OrderItem.objects.select_related('product').filter(order=order)
                    for orderitem in orderitems:
                        orderitem.price = orderitem.product.price
                        product = Product.objects.get(slug=orderitem.product.slug)
                        product.sold += orderitem.quantity
                        orderitem.save()
                        product.save()
                    payment.total = total_cost
                    order.complete = True
                    payment.complete = True
                    order.save()
                    payment.save()
            else:
                if not (len(str(card)) == 8):
                    payment.error_status = True
                    payment.error_msg = 'invalid card number length'
                    payment.save()
                else:
                    payment.error_status = True
                    payment.error_msg = 'the card number is not even'
                    payment.save()
                context['payment'] = payment
                if payment.payment_way == 'ACNT':
                    return render(request, 'cart/paymentsomeone.html', context)
                return render(request, 'cart/payment.html', context)
            return redirect(reverse('payment_procedure'))
    if payment.payment_way == 'ACNT':
        return render(request, 'cart/paymentsomeone.html', context)
    return render(request, 'cart/payment.html', context)


@login_required
def payment_procedure(request):
    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    return render(request, 'cart/progressPayment.html', context)


@login_required
def oneorder(request, pk):
    total_cart_items, total_cost, order = get_total_cart_items(request)
    order = Order.objects.prefetch_related('delivery', 'payment').get(pk=pk)
    orderitems = OrderItem.objects.select_related('product').filter(order=order).order_by('product')
    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['order'] = order
    context['orderitems'] = orderitems
    return render(request, 'cart/oneorder.html', context)
