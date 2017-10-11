from django.contrib import admin
from .models import (
    Profile, Group,
)

admin.site.register((
    Profile, Group,
))

