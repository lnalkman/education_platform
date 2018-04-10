from django.conf.urls import url
from django.views.generic.base import TemplateView

from .views import (
    TeacherProfile, CourseListView, DeleteLesson,
    CourseSettings, CourseDelete, AjaxUpdateCourse,
    CalendarView, CalendarRedirect, CalendarDay,
    CalendarNoteAdd, CalendarNoteDelete, CalendarNoteChange,
    AjaxAddModule, AjaxAddGroupToCourse, AjaxCourseGroups,
    AjaxRemoveCourseGroups, ModuleDetail, AjaxAddLessonForm,
    DeleteModule, AjaxUploadLessonFiles, JsonFileList,
    JsonLessonDetail, LessonUpdate, AjaxDeleteLessonFile,
    BlogView, PublicationView, AddPostView,
    DeletePostView, EditPostView, BlogPostSearchView
)


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),
    # url(r'^course/add/$', AddCourseView.as_view(), name='course-add'),
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
    url(r'^module/(?P<pk>[0-9]+)/$', ModuleDetail.as_view(), name='module-settings'),
    url(r'^module/(?P<pk>[0-9]+)/delete/$', DeleteModule.as_view(), name='module-delete'),
    url(r'^module/(?P<pk>[0-9]+)/lesson/add/$', AjaxAddLessonForm.as_view(), name='lesson-add'),
    url(r'^lesson/(?P<pk>[0-9]+)/file/upload/$', AjaxUploadLessonFiles.as_view(), name='lesson-file-add'),
    url(r'^lesson/(?P<pk>[0-9]+)/file/delete/$', AjaxDeleteLessonFile.as_view(), name='lesson-file-add'),
    url(r'^lesson/(?P<pk>[0-9]+)/files/$', JsonFileList.as_view(), name='lesson-file-list'),
    url(r'^lesson/(?P<pk>[0-9]+)/json/$', JsonLessonDetail.as_view(), name='lesson-detail-json'),
    url(r'^lesson/(?P<pk>[0-9]+)/update/$', LessonUpdate.as_view(), name='lesson-update'),
    url(r'^lesson/(?P<pk>[0-9]+)/delete/$', DeleteLesson.as_view(), name='lesson-delete'),
    url(r'^blog/$', BlogView.as_view(), name='blog'),
    url(r'^blog/post/(?P<pk>[0-9]+)/$', PublicationView.as_view(), name='blog-post'),
    url(r'^blog/post/add/$', AddPostView.as_view(), name='blog-post-add'),
    url(r'^blog/post/(?P<pk>[0-9]+)/delete/$', DeletePostView.as_view(), name='blog-post-delete'),
    url(r'^blog/post/(?P<pk>[0-9]+)/edit/$', EditPostView.as_view(), name='blog-post-edit'),
    url(r'^blog/search/$', BlogPostSearchView.as_view(), name='blog-post-search')
]
