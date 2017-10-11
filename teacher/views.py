from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError
)

from edu_process.models import Profile


class TeacherProfile(DetailView):
    no_permission_message = 'Цю сторінку можуть переглядати лише користувачі з викладацьким типом профілю'
    template_name = 'teacher/teacher-account.html'
    model = Profile

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            try:
                if user.profile.user_type == Profile.TEACHER:
                    return super(DetailView, self).dispatch(request, *args, **kwargs)
                return HttpResponseForbidden(self.no_permission_message)
            except User.profile.RelatedObjectDoesNotExist:
                return HttpResponseServerError('Неможливо отримати доступ до профілю користувача.')

        return HttpResponseRedirect(reverse('index'))

    def get_object(self):
        return self.request.user

