from django.conf.urls import url

from .views import TeacherProfile


urlpatterns = [
    url(r'^$', TeacherProfile.as_view(), name='index'),

]
