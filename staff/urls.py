from django.conf.urls import url
from .views import (
    TeacherAdmin, AjaxTeacherAdmin
)

urlpatterns = [
    url(r'^teachers$', TeacherAdmin.as_view(), name='teachers'),
    url(r'^teachers/ajax$', AjaxTeacherAdmin.as_view(), name='teacher-ajax'),
]