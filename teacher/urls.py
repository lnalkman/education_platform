from django.conf.urls import url

from .views import (
    TeacherProfile, AddCourseView, CourseListView,
    CourseDetail, CalendarView, CalendarRedirect
)


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),
    url(r'^course/add/$', AddCourseView.as_view(), name='course-add'),
    url(r'^courses/$', CourseListView.as_view(), name='course-list'),
    url(r'^course/(?P<pk>[0-9]+)/$', CourseDetail.as_view(), name='course-detail'),
    url(r'^calendar/$', CalendarRedirect.as_view(), name='calendar-redirect'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)/$', CalendarView.as_view(), name='calendar'),
]
