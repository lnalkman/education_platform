from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Profile, Group, Message
)

admin.site.unregister(User)
admin.site.register((
    Group,  Message
))


class ProfileAdmin(admin.StackedInline):
    model = Profile


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [
        ProfileAdmin,
    ]
    list_display = ('colored_username', 'email', 'first_name', 'last_name', 'is_staff' '')
    empty_value_display = '---'

    def colored_username(self, obj):
        if not hasattr(obj, 'profile'):
            return format_html(
                '<span style="color:red">%s</span>' % obj.username
            )
        return obj.username
    colored_username.admin_order_field = 'username'
    colored_username.short_description = _('username')

    def response_add(self, request, obj, post_url_continue=None):
        if not hasattr(obj, 'profile'):
            Profile.objects.create(user=obj)
        return super().response_add(request, obj, post_url_continue)

