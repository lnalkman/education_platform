from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import test

urlpatterns = [
    url(r'^id-(?P<pk>[0-9]+)/$', TemplateView.as_view(template_name='student/student-account.html'), name='profile'),
    url(r'^courses/$', TemplateView.as_view(template_name='student/courses.html'), name='course-list'),
]