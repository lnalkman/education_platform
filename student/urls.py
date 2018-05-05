from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import CoursesView

urlpatterns = [
    url(r'^id-(?P<pk>[0-9]+)/$', TemplateView.as_view(template_name='student/student-account.html'), name='profile'),
    url(r'^courses/$', CoursesView.as_view(), name='course-list'),
]