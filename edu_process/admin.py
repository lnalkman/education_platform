from django.contrib import admin
from .models import (
    Profile, Group, TemporaryUser,
)

admin.site.register((
    Profile, Group, TemporaryUser,
))

