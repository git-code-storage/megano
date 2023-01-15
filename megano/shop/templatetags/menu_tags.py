from django import template
from shop.models import Category


register = template.Library()


@register.inclusion_tag('shop/include/tags/category_menu.html')
def get_categories():
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}
