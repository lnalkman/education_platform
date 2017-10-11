from django.conf.urls import url
from django.views.generic.base import TemplateView
from .views import (
    IndexView,
)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^profile/student/$', TemplateView.as_view(template_name='teacher/teacher-account.html'), name='student-profile'),
]
