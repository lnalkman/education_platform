from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import (
    CoursesView, CalendarView, CalendarRedirect, CalendarDayView,
    StudentAccountView,
)

urlpatterns = [
    url(r'^id-(?P<pk>[0-9]+)/$', StudentAccountView.as_view(), name='profile'),
    url(r'^courses/$', CoursesView.as_view(), name='course-list'),
    url(r'^calendar/$', CalendarRedirect.as_view(), name='calendar-redirect'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)/$', CalendarView.as_view(), name='calendar'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)/$', CalendarDayView.as_view(), name='calendar-day'),
]