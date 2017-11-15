from django.conf.urls import url

from .views import (
    TeacherProfile, AddCourseView, CourseListView,
    CourseDetail, CalendarView, CalendarRedirect,
    CalendarDay, CalendarNoteAdd, CalendarNoteDelete,
    CalendarNoteChange,
)


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),
    url(r'^course/add/$', AddCourseView.as_view(), name='course-add'),
    url(r'^courses/$', CourseListView.as_view(), name='course-list'),
    url(r'^course/(?P<pk>[0-9]+)/$', CourseDetail.as_view(), name='course-detail'),
    url(r'^calendar/$', CalendarRedirect.as_view(), name='calendar-redirect'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)/$', CalendarView.as_view(), name='calendar'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)/$', CalendarDay.as_view(template_name='teacher/calendar-day.html'), name='calendar-day'),
    url(r'^calendar/note/add/$', CalendarNoteAdd.as_view(), name='calendar-note-add'),
    url(r'^calendar/note/delete/$', CalendarNoteDelete.as_view(), name='calendar-note-delete'),
    url(r'^calendar/note/change/$', CalendarNoteChange.as_view(), name='calendar-note-change'),
]
