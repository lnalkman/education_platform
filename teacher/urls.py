from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import (
    TeacherProfile, AddCourseView, CourseListView,
    CourseSettings, CourseDelete, AjaxUpdateCourse,
    CalendarView, CalendarRedirect, CalendarDay,
    CalendarNoteAdd, CalendarNoteDelete, CalendarNoteChange,
    AjaxAddModule, AjaxAddGroupToCourse, AjaxCourseGroups,
    AjaxRemoveCourseGroups,
)


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),
    url(r'^course/add/$', AddCourseView.as_view(), name='course-add'),
    url(r'^courses/$', CourseListView.as_view(), name='course-list'),
    url(r'^course/(?P<pk>[0-9]+)/$', CourseSettings.as_view(), name='course-settings'),
    url(r'^course/(?P<pk>[0-9]+)/delete/$', CourseDelete.as_view(), name='course-delete'),
    url(r'^course/(?P<pk>[0-9]+)/update/$', AjaxUpdateCourse.as_view(), name='course-update'),
    url(r'^course/(?P<pk>[0-9]+)/add/module/$', AjaxAddModule.as_view(), name='course-module-add'),
    url(r'^course/(?P<pk>[0-9]+)/add/group/$', AjaxAddGroupToCourse.as_view(), name='group-to-course-add'),
    url(r'^course/(?P<pk>[0-9]+)/groups/$', AjaxCourseGroups.as_view(), name='course-group-list'),
    url(r'^course/(?P<pk>[0-9]+)/groups/remove/$', AjaxRemoveCourseGroups.as_view(), name='course-group-remove'),
    url(r'^calendar/$', CalendarRedirect.as_view(), name='calendar-redirect'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)/$', CalendarView.as_view(), name='calendar'),
    url(r'^calendar/(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)/$', CalendarDay.as_view(template_name='teacher/calendar-day.html'), name='calendar-day'),
    url(r'^calendar/note/add/$', CalendarNoteAdd.as_view(), name='calendar-note-add'),
    url(r'^calendar/note/delete/$', CalendarNoteDelete.as_view(), name='calendar-note-delete'),
    url(r'^calendar/note/change/$', CalendarNoteChange.as_view(), name='calendar-note-change'),
]
