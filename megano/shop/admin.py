from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.utils import ProgrammingError
from mptt.admin import MPTTModelAdmin
from .models import *


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):

    list_display = ('name', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = ('user', 'product', 'feedback', 'score',)
    list_filter = ('user', 'product', 'score',)
    search_fields = ('user', 'product',)
    ordering = ('creation_date',)
    readonly_fields = ('user', 'product', 'feedback', 'score',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = ('id', 'order', 'payment_way', 'date_of_creation', 'date_of_update', 'complete', 'error_status',
                    'error_msg',)
    list_filter = ('payment_way', 'complete', 'error_status',)
    search_fields = ('order', )
    readonly_fields = ('date_of_creation', 'date_of_update',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = ('order', 'product', 'price', 'quantity', 'date_added',)
    search_fields = ('order', 'product', 'date_added',)
    readonly_fields = ('date_added',)


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_of_creation', 'date_of_changing', 'complete',)
    list_filter = ('complete',)
    search_fields = ('id', 'customer', 'date_of_creation',)
    readonly_fields = ('date_of_creation', 'date_of_changing',)
    inlines = [OrderItemInline]


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'comment', 'type_of_delivery', 'complete',)
    list_filter = ('type_of_delivery', 'complete',)
    search_fields = ('order', 'address',)


@admin.register(TypeOfDelivery)
class TypeOfDeliveryAdmin(admin.ModelAdmin):
    list_display = ('type_of_delivery', 'min_order', 'cost', 'additional_cost',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_product_name',)
    fieldsets = [[None, {'fields': ['product', 'get_image', 'image', ]}]]
    readonly_fields = ('get_image',)

    def get_product_name(self, obj):
        return obj.product.name

    def get_image(self, obj):
        if obj.image.url:
            return mark_safe(f'<img src={obj.image.url} width="20%">')

    get_image.short_description = 'View'
    get_product_name.short_description = 'Product'


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    fieldsets = [[None, {'fields': ['get_image', 'image', ]}]]
    readonly_fields = ('get_image',)

    def get_image(self, obj):
        if obj.image.url:
            return mark_safe(f'<img src={obj.image.url} width="20%">')

    get_image.short_description = 'View'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'amount', 'category', 'is_limited', 'index', 'is_active',)
    list_filter = ('category', 'is_limited', 'is_active',)
    fieldsets = (
        ('Technical data', {'fields': ('name', 'slug', 'category', 'short_description', 'description', 'creation_date',
                                       'update_date', 'get_big_image', 'image')}),
        ('Commercial data', {'fields': ('price', 'amount', 'sold', 'index')}),
        ('Status', {'fields': ('is_limited', 'is_active')}),
    )

    readonly_fields = ('creation_date', 'update_date', 'get_big_image',)
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def get_big_image(self, obj):
        if obj.image.url:
            return mark_safe(f'<img src={obj.image.url} width="20%">')

    get_big_image.short_description = 'Main view'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # Create a default object on the first page of SiteSettingsAdmin with a list of settings
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # be sure to wrap the loading and saving SiteSettings in a try catch,
        # so that you can create database migrations
        try:
            SiteSettings.load().save()
        except ProgrammingError:
            pass

    # prohibit adding new settings
    def has_add_permission(self, request, obj=None):
        return False

    # as well as deleting existing
    def has_delete_permission(self, request, obj=None):
        return False
