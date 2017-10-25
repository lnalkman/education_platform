from django.conf.urls import url
from .views import (
    TeacherAdmin,
)

urlpatterns = [
    url(r'^teachers$', TeacherAdmin.as_view(), name='teachers')
]