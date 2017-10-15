from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from edu_process.models import Profile
from .models import Course
from .forms import CourseForm


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


class AddCourseView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """View для додавання курсів. Доступний тільки для вчителів."""
    template_name = 'teacher/course-edit.html'
    form_class = CourseForm
    success_url = '/teacher/course/'
    login_url = '/'

    def test_func(self):
        return self.request.user.profile.is_teacher()

    def form_valid(self, form):
        """Додаємо поле з автором вручну і зберігаємо"""
        form.cleaned_data['author'] = self.request.user.profile
        Course.objects.create(**form.cleaned_data)
        return super(FormView, self).form_valid(form)
