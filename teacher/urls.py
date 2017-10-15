from django.conf.urls import url

from .views import TeacherProfile, AddCourseView


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),
    url(r'^course/add/$', AddCourseView.as_view(), name='course-add'),
]
