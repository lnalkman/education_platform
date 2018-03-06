from django.conf.urls import url
from django.views.generic.base import TemplateView
from .views import (
    IndexView, SearchGroup, MessagesApiView, MessageView,
    MessageUserApiView
)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^group/search/$', SearchGroup.as_view(), name='search-group'),
    url(r'^profile/student/$', TemplateView.as_view(template_name='teacher/teacher-account.html'), name='student-profile'),
    url(r'^messages/$', MessageView.as_view(), name='messages'),
    url(r'^api/messages/list/', MessagesApiView.as_view()),
    url(r'^api/messages/users', MessageUserApiView.as_view())
]
