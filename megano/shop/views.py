import logging

from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db.models import Q, Min, Max
from django.views.generic import DetailView
from .utils import get_total_cart_items
from .models import Product, Order, OrderItem, Category, Delivery, TypeOfDelivery, Payment, ProductImage
from user.models import DeliveryAddress
from .filters import ProductFilter
from .forms import DeliveryForm, ChoicePaymentForm, CardForm
from user.utils import registration_base
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.views.generic import ListView


logger = logging.getLogger(__name__)
#logger.info(f'shop.views')


def index(request):
    q = Q(is_active=True) & Q(amount__gt=0)
    items = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    q = Q(is_active=True) & Q(amount__gt=0) & Q(is_limited=True)
    is_limited = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    products = items[:4]
    products_hide_md = items[5:7]
    products_hide_1450 = items[7:9]
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context = {
        'products': products,
        'products_hide_md': products_hide_md,
        'products_hide_1450': products_hide_1450,
        'is_limited': is_limited,
        'total_cart_items': total_cart_items,
        'total_cost': total_cost,
    }
    return render(request, 'shop/index.html', context=context)


def add_cart(request, product_slug, amt, referer=None):
    if request.user.is_anonymous:
        if 'cart' in request.session:
            if product_slug not in request.session['cart'].keys():
                request.session['cart'][product_slug] = amt
                request.session.modified = True
            else:
                request.session['cart'][product_slug] += amt
                request.session.modified = True
        else:
            request.session['cart'] = {product_slug: amt, }
            request.session.modified = True
    else:
        product = Product.objects.get(slug=product_slug)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        order.save()
        orderitem, created = OrderItem.objects.get_or_create(
            product=product,
            order=order,
        )
        orderitem.quantity += amt
        orderitem.save()
    if not referer:
        referer = request.META.get('HTTP_REFERER')
    return redirect(referer)


def add_cart_from_cookies(request, product_slug):
    if 'amount' in request.COOKIES:
        if int(request.COOKIES.get('amount')) > 0:
            amt = int(request.COOKIES.get('amount'))
            referer = request.META.get('HTTP_REFERER')
            return add_cart(request, product_slug, amt, referer=referer)


def remove_cart(request, product_slug):
    if request.user.is_anonymous:
        if 'cart' in request.session:
            if product_slug in request.session['cart'].keys():
                request.session['cart'][product_slug] -= 1
                if request.session['cart'][product_slug] == 0:
                    del request.session['cart'][product_slug]
                request.session.modified = True
    else:
        product = Product.objects.get(slug=product_slug)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        orderitem = OrderItem.objects.get(
            product=product,
            order=order,
        )
        if orderitem:
            if orderitem.quantity > 0:
                orderitem.quantity -= 1
                orderitem.save()
            else:
                orderitem.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def remove_product_cart(request, product_slug):
    if request.user.is_anonymous:
        if 'cart' in request.session:
            if product_slug in request.session['cart'].keys():
                del request.session['cart'][product_slug]
                request.session.modified = True
    else:
        product = Product.objects.get(slug=product_slug)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        orderitem = OrderItem.objects.get(
            product=product,
            order=order,
        )
        if orderitem:
            orderitem.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def cart(request):
    total = 0

    if request.user.is_authenticated:
        total_cart_items, total_cost, order = get_total_cart_items(request)
        in_cart = OrderItem.objects.select_related('product').filter(order=order)
    else:
        in_cart = []
        if 'cart' in request.session:
            total_cart_items, total_cost, queryset = get_total_cart_items(request)
            for product in queryset:
                in_cart.append((product, request.session['cart'][product.slug]))
                total += product.price * request.session['cart'][product.slug]

    context = dict()
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['in_cart'] = in_cart
    context['total'] = total_cost

    return render(request, 'shop/cart.html', context)


def products_by_category(request, category_slug, sort):

    # if the function receives the 'sort_by' parameter in the GET request,
    # it is redirected to the corresponding sorting page

    if request.META.get('HTTP_REFERER'):
        refer_list = request.META.get('HTTP_REFERER').split('/')
        if len(refer_list) == 7:
            filters = refer_list[6]
    else:
        filters = ''
    if request.GET.get('sort_by'):
        sort = request.GET.get('sort_by')
        return redirect(f'../../{category_slug}/{sort}/{filters}')

    # можно упростить
    q = Q(is_active=True) & Q(amount__gt=0) & Q(category__slug=category_slug)
    if sort == 'cost_asc':
        ordering = 'price'
    elif sort == 'cost_desc':
        ordering = '-price'
    elif sort == 'pop_asc':
        ordering = 'sold'
    elif sort == 'pop_desc':
        ordering = '-sold'
    elif sort == 'new_asc':
        ordering = 'creation_date'
    elif sort == 'new_desc':
        ordering = '-creation_date'
    elif sort == 'feed_asc':
        ordering = 'index'
    elif sort == 'feed_desc':
        ordering = '-index'
    else:
        ordering = 'price'

    queryset = Product.objects.filter(q).order_by(ordering)
    result = queryset.aggregate(Min('price'), Max('price'))

    product_filter = ProductFilter(request.GET, queryset=queryset)
    queryset = product_filter.qs

    paginator = Paginator(queryset, 8)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)

    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    context['sort'] = sort
    context['products'] = page.object_list
    context['page'] = page
    context['price_min'] = int(result['price__min'])
    context['price_max'] = int(result['price__max']) + 1
    if request.GET.get('price_range'):
        value_list = request.GET.get('price_range').split(';')
        context['price_from'] = int(value_list[0])
        context['price_to'] = int(value_list[1])
    else:
        context['price_from'] = context['price_min']
        context['price_to'] = context['price_max']
    if request.GET.get('onhand') == 'on':
        context['onhand'] = 'checked'
    else:
        context['onhand'] = ''
    if request.GET.get('freedelivery') == 'on':
        context['freedelivery'] = 'checked'
    else:
        context['freedelivery'] = ''
    category = Category.objects.get(slug=category_slug)
    context['category'] = category
    return render(request, 'shop/catalog.html', context)


class ProductDetailView(DetailView):

    model = Product
    context_object_name = 'product'
    template_name = 'shop/product.html'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        total_cart_items, total_cost, order = get_total_cart_items(self.request)
        context['total_cart_items'] = total_cart_items
        context['total_cost'] = total_cost
        product = Product.objects.get(slug=self.kwargs.get("product_slug"))
        product_pictures = ProductImage.objects.filter(product=product)[:7]
        context['product_pictures'] = product_pictures
        return context


def order_step_one(request):

    check_succsess, context = registration_base(request, 'oder_one_step')
    if check_succsess:
        return redirect(reverse('oder_one_step'))
    return render(request, 'shop/order_one.html', context)


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
            return render(request, 'shop/order_two.html', context)
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
    return render(request, 'shop/order_two.html', context)


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
            return render(request, 'shop/order_two.html', context)
    else:
        form = ChoicePaymentForm()
        payment, created = Payment.objects.get_or_create(order=order, complete=False)
        context['payment_way'] = payment.payment_way
        context['form'] = form
    return render(request, 'shop/order_three.html', context)


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

    return render(request, 'shop/order_four.html', context)


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
                    return render(request, 'shop/paymentsomeone.html', context)
                return render(request, 'shop/payment.html', context)
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
                    return render(request, 'shop/paymentsomeone.html', context)
                return render(request, 'shop/payment.html', context)
            return redirect(reverse('payment_procedure'))
    if payment.payment_way == 'ACNT':
        return render(request, 'shop/paymentsomeone.html', context)
    return render(request, 'shop/payment.html', context)


@login_required
def payment_procedure(request):
    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    return render(request, 'shop/progressPayment.html', context)


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
    return render(request, 'shop/oneorder.html', context)


class SearchResultsView(ListView):
    model = Product
    template_name = 'shop\search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = Product.objects.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        total_cart_items, total_cost, order = get_total_cart_items(self.request)
        context['total_cart_items'] = total_cart_items
        context['total_cost'] = total_cost
        return context


def about(request):
    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    return render(request, 'shop/about.html', context)