import logging
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import Q, Min, Max
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from .utils import get_total_cart_items
from .models import Product, Order, OrderItem, Category
from .filters import ProductFilter
from .forms import CommentForm, AuthCommentForm
from django.views.generic import ListView


logger = logging.getLogger(__name__)
#logger.info(f'shop.views')


def index(request):
    q = Q(is_active=True) & Q(amount__gt=0)
    items = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    q = Q(is_active=True) & Q(amount__gt=0) & Q(is_limited=True)
    is_limited = Product.objects.select_related('category').filter(q).order_by('-index', '-sold')
    top_categories = Category.objects.filter(is_favourites=True)
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
        'top_categories': top_categories,
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
    queryset = Product.objects.filter(q).order_by(sort)
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


class ProductDetailView(FormMixin, DetailView):

    model = Product
    context_object_name = 'product'
    template_name = 'shop/product.html'
    slug_url_kwarg = 'product_slug'
    auth_form_class = AuthCommentForm
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.product = self.get_object()
        if self.request.user.is_authenticated:
            comment.user = self.request.user
            comment.name = self.request.user.name
            comment.email = self.request.user.email
        comment.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        total_cart_items, total_cost, order = get_total_cart_items(self.request)
        context['total_cart_items'] = total_cart_items
        context['total_cost'] = total_cost
        product = Product.objects.prefetch_related('feedback_set', 'productimage_set').get(slug=self.kwargs.get("product_slug"))
        product_pictures = product.productimage_set.all()[:7]
        feedbacks = product.feedback_set.all()
        feedbacks.length = len(product.feedback_set.all())
        context['product_pictures'] = product_pictures
        context['feedbacks'] = feedbacks
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('product_detail', kwargs={'product_slug': self.get_object().slug})

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return self.auth_form_class
        else:
            return self.form_class


class SearchResultsView(ListView):
    model = Product
    template_name = 'shop\search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('query')
        q = Q(is_active=True) & Q(name__icontains=query)
        queryset = Product.objects.filter(q)
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

def blog(request):
    context = dict()
    total_cart_items, total_cost, order = get_total_cart_items(request)
    context['total_cart_items'] = total_cart_items
    context['total_cost'] = total_cost
    return render(request, 'shop/sale.html', context)
