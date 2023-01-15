from .models import *


def get_total_cart_items(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total_cost, total_cart_items = order.get_cart_total_and_items

    else:
        total_cart_items = 0
        total_cost = 0
        if 'cart' in request.session.keys():
            products = request.session['cart'].keys()
            for product in products:
                amount = request.session['cart'][product]
                total_cart_items += request.session['cart'][product]
                price = Product.objects.get(slug=product).price
                total_cost += price * amount
    return total_cart_items, total_cost


