from django.conf.urls import url
from django.views.generic.base import TemplateView
from .views import (
    IndexView, SearchGroup, MessagesApiView, MessageView,
    MessageUserApiView, UserAvatarView, LogoutView, CourseListJsonView,
    CourseView, LessonJsonView, GlobalSearchView
)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^group/search/$', SearchGroup.as_view(), name='search-group'),
    url(r'^messages/$', MessageView.as_view(), name='messages'),
    url(r'^api/messages/list/$', MessagesApiView.as_view()),
    url(r'^api/messages/users/$', MessageUserApiView.as_view()),
    url(r'^api/course/$', CourseListJsonView.as_view()),
    url(r'^avatar/$', UserAvatarView.as_view(), name='user-avatar'),
    url(r'^auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^course/(?P<pk>[0-9]+)/$', CourseView.as_view(), name='course-detail'),
    url(r'^search/$', GlobalSearchView.as_view(), name='search'),
    url(r'lesson/(?P<pk>[0-9]+)/json/$', LessonJsonView.as_view(), name='lesson-detail-json'),

]
