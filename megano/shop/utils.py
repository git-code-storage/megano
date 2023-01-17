from .models import Order, Product, TypeOfDelivery
import logging

logger = logging.getLogger(__name__)


def get_total_cart_items(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.select_related('payment', 'delivery', 'delivery__type_of_delivery').get_or_create(customer=customer, complete=False)
        total_cost, total_cart_items = order.get_cart_total_and_items
        order.save()
        delivery = order.delivery
        if delivery and total_cost > 0:
            if total_cost < delivery.type_of_delivery.min_order:
                total_cost += delivery.type_of_delivery.cost
            if delivery.type_of_delivery.type_of_delivery == 'EXPRESS':
                total_cost += delivery.type_of_delivery.additional_cost
        return total_cart_items, total_cost, order
    else:
        total_cart_items = 0
        total_cost = 0
        order = None
        if 'cart' in request.session.keys():
            products_keys = request.session['cart'].keys()
            products = Product.objects.filter(slug__in=products_keys)
            for product in products:
                amount = request.session['cart'][product.slug]
                total_cart_items += request.session['cart'][product.slug]
                total_cost += product.price * amount
            normal_delivery = TypeOfDelivery.objects.get(type_of_delivery='NORMAL')
            logger.info(f'normal_delivery - {normal_delivery.type_of_delivery}')
            if total_cost < normal_delivery.min_order:
                total_cost += normal_delivery.cost
            return total_cart_items, total_cost, products


