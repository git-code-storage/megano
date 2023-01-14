from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, DeliveryAddress


class DeliveryAddressInline(admin.StackedInline):
    model = DeliveryAddress
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = ('email', 'name', 'phone', 'is_staff', 'is_active', 'date_of_registration')
    list_filter = ('email', 'phone', 'is_staff', 'is_active',)
    fieldsets = (
        ('Personal data', {'fields': ('email', 'phone', 'name', 'password', 'avatar',
                                      'get_big_avatar')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'is_staff', 'is_active', 'avatar')}
        ),
    )
    search_fields = ('email', 'phone',)
    ordering = ('email',)
    readonly_fields = ('get_small_avatar', 'get_big_avatar',)
    inlines = [DeliveryAddressInline]

    def get_small_avatar(self, obj):
        if obj.avatar.url:
            return mark_safe(f'<img src={obj.avatar.url} width="50" height="60">')

    def get_big_avatar(self, obj):
        if obj.avatar.url:
            return mark_safe(f'<img src={obj.avatar.url} width="200" height="240">')


    get_small_avatar.short_description = 'Avatar view'
    get_big_avatar.short_description = 'Avatar view'


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):

    list_display = ('user', 'city', 'address',)
    list_filter = ('city',)
    search_fields = ('user', 'city', 'address',)
    ordering = ('user',)
