from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError
)
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from edu_process.models import Profile
from .models import Course
from .forms import CourseForm


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Надає доступ до сторінки тільки викладачам"""
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.profile.is_teacher()


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

    def get_object(self, queryset=None):
        return self.request.user


class AddCourseView(TeacherRequiredMixin, FormView):
    """View для додавання курсів. Доступний тільки для вчителів."""
    template_name = 'teacher/course-edit.html'
    form_class = CourseForm
    success_url = '/teacher/course/'

    def form_valid(self, form):
        """Додаємо поле з автором вручну і зберігаємо"""
        form.cleaned_data['author'] = self.request.user.profile
        Course.objects.create(**form.cleaned_data)
        return super(FormView, self).form_valid(form)


class CourseListView(TeacherRequiredMixin, ListView):
    template_name = 'teacher/course-list.html'

    def get_queryset(self):
        return self.request.user.profile.course_set.all()


class CourseDetail(TeacherRequiredMixin, UpdateView):
    template_name = 'teacher/course-detail.html'
    form_class = CourseForm

    def test_func(self):
        """Перевірка чи є користувач викладачем і чи належить запитуваний курс йому"""
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def get_object(self, queryset=None):
        return self.request.user.profile.course_set.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['modules_list'] = self.object.module_set.all()
        return context
