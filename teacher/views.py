from calendar import HTMLCalendar
from calendar import month_name
from datetime import datetime, timedelta
from functools import partial

from django.urls import reverse_lazy
from django.shortcuts import reverse
from django.views.generic.edit import UpdateView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.base import TemplateView, RedirectView, View
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core import serializers

from edu_process.models import Group
from .models import Course, CalendarNote, Module
from .forms import (
    CourseForm, TeacherProfileForm, CalendarNoteForm,
    ModuleForm, LessonForm, Lesson
)


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Надає доступ до сторінки тільки викладачам"""
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.profile.is_teacher()


class TeacherProfile(TeacherRequiredMixin, UpdateView):
    template_name = 'teacher/teacher-account.html'
    form_class = TeacherProfileForm

    def form_valid(self, form):
        form.save()
        return super(UpdateView, self).form_valid()

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_upcoming_events(self):
        now = datetime.now().date()
        return CalendarNote.objects.filter(
            author=self.request.user.profile,
            date__date__gt=now,
            date__date__lte=now + timedelta(days=7)
        )[:4]

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['upcoming_events'] = self.get_upcoming_events()
        return context


class AddCourseView(TeacherRequiredMixin, FormView):
    """View для додавання курсів. Доступний тільки для вчителів."""
    template_name = 'teacher/course-add.html'
    form_class = CourseForm
    success_url = '/teacher/courses/'

    def form_valid(self, form):
        """Додаємо поле з автором вручну і зберігаємо"""
        form.cleaned_data['author'] = self.request.user.profile
        Course.objects.create(**form.cleaned_data)
        return super(FormView, self).form_valid(form)


class CourseListView(TeacherRequiredMixin, ListView):
    template_name = 'teacher/course-list.html'

    def get_queryset(self):
        return self.request.user.profile.course_set.all()


class CourseSettings(TeacherRequiredMixin, UpdateView):
    template_name = 'teacher/course-settings.html'
    form_class = CourseForm
    context_object_name = 'Course'

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
        context['module_list'] = self.object.module_set.all()
        context['calendar_note_list'] = self.object.calendarnote_set.all()
        context['update_form'] = CourseForm(instance=self.object)
        context['add_module_form'] = ModuleForm(initial={'course': self.object})
        return context


class AjaxUpdateCourse(TeacherRequiredMixin, View):
    http_method_names = ('post',)
    form = CourseForm

    def test_func(self):
        """Перевірка чи є користувач викладачем і чи належить запитуваний курс йому"""
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def render_to_json(self, data):
        return JsonResponse(data)

    def form_valid(self, form):
        Course.objects.filter(pk=self.kwargs['pk']).update(
            **form.cleaned_data
        )
        return self.render_to_json({'success': True})

    def form_invalid(self, form):
        data = {
            'success': False,
            'errors': form.errors.as_json()
        }
        return self.render_to_json(data)

    def post(self, request, *args, **kwargs):
        form = self.form(self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class CourseDelete(TeacherRequiredMixin, RedirectView):
    http_method_names = ('post',)
    url = reverse_lazy('teacher:course-list')

    def test_func(self):
        """
        Перевірка чи є користувач викладачем і чи належить курс йому
        """
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def post(self, request, *args, **kwargs):
        Course.objects.get(pk=kwargs['pk']).delete()
        return RedirectView.post(self, request, *args, **kwargs)


class AjaxAddModule(TeacherRequiredMixin, View):
    http_method_names = ('post',)
    form = ModuleForm

    def test_func(self):
        """Перевірка чи є користувач викладачем і чи належить запитуваний курс йому"""
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def can_add(self, obj):
        if obj.course.author == self.request.user.profile:
            return True

    def render_to_json(self, data):
        return JsonResponse(data)

    def form_valid(self, form):
        obj = form.save(commit=False)
        if self.can_add(obj):
            obj.save()
            return self.render_to_json({'success': True})
        form.add_error(field=None, error='У вас немає прав додавати модуль до цього курсу')
        return self.form_invalid(form)

    def form_invalid(self, form):
        data = {
            'success': False,
            'errors': form.errors.as_json()
        }
        return self.render_to_json(data)

    def post(self, request, *args, **kwargs):
        form = self.form(self.request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class AjaxAddGroupToCourse(TeacherRequiredMixin, View):
    http_method_names = ('post',)

    def test_func(self):
        """Перевірка чи є користувач викладачем і чи належить запитуваний курс йому"""
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def get_course(self, pk):
        return Course.objects.get(pk=pk)

    def get_group(self, name):
        group = None
        try:
            group = Group.objects.get(name=name)
        finally:
            return group

    def add_group(self, group, course):
        if not group:
            return 'Невірно задана група'
        if not course:
            return 'Невірне значення курсу'

        try:
            course.group_set.add(group)
        except Exception as e:
            return str(e)

    def render_to_json(self, error=None):
        return JsonResponse({
            'error': error
        })

    def post(self, request, *args, **kwargs):
        course_pk = kwargs['pk']
        group_name = request.POST.get('group_name', 0)

        group = self.get_group(group_name)
        course = self.get_course(course_pk)
        error = self.add_group(group, course)
        return self.render_to_json(error)


class AjaxCourseGroups(View):
    http_method_names = ('get',)

    def get_course(self, course_pk):
        obj = None
        try:
            obj = Course.objects.filter(pk=course_pk)
        finally:
            return obj

    def get_queryset(self, course_pk):
        queryset = None
        try:
            queryset = Course.objects.get(pk=course_pk).group_set.all()
        finally:
            return queryset

    def render_to_json(self):
        json = """{{
            "course": {:},
            "groups": {:}
        }}""".format(
            serializers.serialize('json', self.course, fields=('name',)),
            serializers.serialize('json', self.queryset, fields=('name',)),
        )

        return HttpResponse(json)

    def get(self, request, *args, **kwargs):
        self.course = self.get_course(kwargs['pk'])
        self.queryset = self.get_queryset(kwargs['pk'])

        return self.render_to_json()


class AjaxRemoveCourseGroups(TeacherRequiredMixin, View):
    http_method_names = ('post',)

    def test_func(self):
        """Перевірка чи є користувач викладачем і чи належить запитуваний курс йому"""
        return (
            TeacherRequiredMixin.test_func(self)
            and self.request.user.profile.course_set.filter(pk=self.kwargs['pk']).exists()
        )

    def get_course(self):
        return Course.objects.get(pk=self.kwargs['pk'])

    def get_queryset(self, pk_list):
        queryset = None
        try:
            queryset = self.course.group_set.filter(pk__in=pk_list)
        finally:
            return queryset

    def remove_groups(self):
        self.course.group_set.remove(
            *self.queryset
        )

    def render_to_json(self, error=''):
        return JsonResponse({'error': error})

    def post(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk_list[]')
        self.course = self.get_course()
        self.queryset = self.get_queryset(pk_list)

        if self.queryset:
            self.remove_groups()

        return self.render_to_json()


class ModuleDetail(TeacherRequiredMixin, DetailView):
    template_name = 'teacher/module-settings.html'
    model = Module
    context_object_name = 'Module'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['lesson_form'] = LessonForm()
        return context


class DeleteModule(TeacherRequiredMixin, RedirectView):
    http_method_names = ('post',)

    def get_redirect_url(self, *args, **kwargs):
        if self.course_pk:
            return reverse(
                'teacher:course-settings',
                kwargs={'pk': self.course_pk}
            )
        return reverse(
            'teacher:module-settings',
            kwargs={'pk': self.kwargs['pk']}
        )

    def can_delete(self, obj):
        return obj.course.author == self.request.user.profile

    def delete_module(self, pk):
        try:
            obj = Module.objects.get(pk=pk)
            self.course_pk = obj.course.pk
        except Module.DoesNotExist:
            pass
        else:
            if self.can_delete(obj):
                obj.delete()

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        self.course_pk = None
        if pk:
            self.delete_module(pk)

        return super(RedirectView, self).post(request, *args, **kwargs)

class AjaxAddLessonForm(TeacherRequiredMixin, View):
    http_method_names = ('post',)
    form = LessonForm
    model = Lesson

    def can_add(self):
        try:
            self.module = Module.objects.get(pk=self.kwargs['pk'])
        except Module.DoesNotExist:
            return False
        return self.module.course.author == self.request.user.profile

    def form_valid(self, form):
        if self.can_add():
            Lesson.objects.create(
                module=self.module,
                **form.cleaned_data
            )
            return self.render_to_json({'status': 1})
        else:
            form.add_error(None, 'У вас немає прав на додавання уроків до цього модулю')
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_json({
            'status': 0,
            'errors': form.errors,
        })

    def render_to_json(self, data):
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class DeleteLesson(TeacherRequiredMixin, RedirectView):
    http_method_names = ('post',)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'teacher:lesson-settings',
            kwargs={'pk': self.kwargs['pk']}
        )

    def can_delete(self, obj):
        return obj.module.course.author == self.request.user.profile

    def delete_lesson(self, pk):
        try:
            obj = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            pass
        else:
            if self.can_delete(obj):
                obj.delete()

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        if pk:
            self.delete_lesson(pk)

        return super(RedirectView, self).post(request, *args, **kwargs)


class HrefCalendar(HTMLCalendar):
    # Якщо в цей день є якісь події/нотатки
    booked_class = 'booked'

    def __init__(self, theyear, themonth, prew_url='#', next_url='#', booked_days=None):
        """:booked_days -> контейнер в якому зберігаються дні в місяці в яких є якісь нотатки"""
        HTMLCalendar.__init__(self)
        self.theyear = theyear
        self.themonth = themonth
        self.prew_url = prew_url
        self.next_url = next_url
        self.booked_days = booked_days

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="month">' \
               '<a href="%s" class="glyphicon glyphicon-chevron-left"></a>' \
               '%s' \
               '<a href="%s" class="glyphicon glyphicon-chevron-right"></a>' \
               '</th></tr>' % (self.prew_url, s, self.next_url)

    def formatday(self, day, weekday, booked=False):

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s %s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday],
                                                                   self.booked_class if booked else '',
                                                                   reverse(
                                                                       'teacher:calendar-day',
                                                                        kwargs={
                                                                            'year': self.theyear,
                                                                            'month': self.themonth,
                                                                            'day': day
                                                                        }
                                                                   ),
                                                                   day
                                                                   )

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, d in self.booked_days) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear=None, themonth=None, withyear=False):
        return HTMLCalendar.formatmonth(
            self,
            theyear or self.theyear,
            themonth or self.themonth,
            withyear
        )


class CalendarView(TeacherRequiredMixin, TemplateView):
    http_method_names = ('get',)
    template_name = 'teacher/calendar.html'

    def get(self, *args, **kwargs):
        try:
            year, month = int(kwargs.get('year', 0)), int(kwargs.get('month', 0))
            if not (isinstance(year, int) and isinstance(month, int)
                    and 1995 < year < 2500 and 0 < month <= 12):
                raise ValueError('Invalid year or month value.')
        except ValueError:
            return HttpResponseRedirect(reverse('calendar-redirect'))
        return TemplateView.get(self, *args, **kwargs)

    def get_booked_days(self, year, month):
        """Повертає множину днів заданого року та місяця у яких є події цього викладача"""
        return {q.date.day for q in CalendarNote.objects.filter(
            author=self.request.user.profile,
            date__year=year,
            date__month=month
        )}

    def get_prev_month_url(self, year, month):
        """Повертає посилання не попередній місяць"""
        if month == 1:
            return reverse('teacher:calendar', kwargs={'year': year - 1, 'month': 12})
        return reverse('teacher:calendar', kwargs={'year': year, 'month': month - 1})

    def get_next_month_url(self, year, month):
        """Повертає посилання не наступний місяць"""
        if month == 12:
            return reverse('teacher:calendar', kwargs={'year': year + 1, 'month': 1})
        return reverse('teacher:calendar', kwargs={'year': year, 'month': month + 1})

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['curr_year'], context['curr_month'] = datetime.now().timetuple()[:2]
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        context['year'], context['month'] = year, month
        context['prev_month_url'] = self.get_prev_month_url(year, month)
        context['next_month_url'] = self.get_next_month_url(year, month)

        booked_days = self.get_booked_days(year, month)
        context['calendar_table'] = HrefCalendar(
            theyear=year,
            themonth=month,
            prew_url=self.get_prev_month_url(year, month),
            next_url=self.get_next_month_url(year, month),
            booked_days=booked_days,
        ).formatmonth()

        return context


class CalendarRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.GET:
            try:
                year, month = int(self.request.GET.get('year', 0)), int(self.request.GET.get('month', 0))
                if not (1995 < year < 2500 and 0 < month <= 12):
                    year, month = datetime.now().timetuple()[:2]
            except ValueError:
                year, month = datetime.now().timetuple()[:2]
        else:
            year, month = datetime.now().timetuple()[:2]
        return reverse('teacher:calendar', kwargs={'year': year, 'month': month})


class CalendarDay(TeacherRequiredMixin, ListView):

    def get_queryset(self):
        return CalendarNote.objects.filter(
            author=self.request.user.profile,
            date__year=self.kwargs['year'],
            date__month=self.kwargs['month'],
            date__day=self.kwargs['day']
        )

    def get_add_form(self):
        return CalendarNoteForm(
            initial={'author': self.request.user.profile},
            date=datetime(year=int(self.kwargs['year']),
                          month=int(self.kwargs['month']),
                          day=int(self.kwargs['day']))
        )

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['form_add'] = self.get_add_form()
        context['month_url'] = reverse('teacher:calendar', kwargs={
            'year': self.kwargs['year'],
            'month': self.kwargs['month']
        })
        context['day_url'] = reverse(
            'teacher:calendar-day',
            kwargs={
                'year': self.kwargs['year'],
                'month': self.kwargs['month'],
                'day': self.kwargs['day']
            }
        )

        return context


class CalendarNoteAdd(TeacherRequiredMixin, RedirectView):
    http_method_names = ('post',)

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get('next_to')
        if url:
            return url
        return reverse('teacher:calendar-redirect')

    def post(self, *args, **kwargs):
        form = CalendarNoteForm(self.request.POST, initial={'author': self.request.user.profile})
        if form.is_valid():
            CalendarNote.objects.create(
                **form.cleaned_data,
            )

        return RedirectView.post(self, *args, **kwargs)


class CalendarNoteDelete(TeacherRequiredMixin, RedirectView):
    http_method_names = ('post',)
    model = CalendarNote

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get('next_to')
        if url:
            return url
        return reverse('teacher:calendar-redirect')

    def can_delete(self, obj):
        return self.request.user.profile == obj.author

    def delete_object(self, pk):
        obj = self.model.objects.get(pk=pk)
        if self.can_delete(obj):
            obj.delete()
            return True
        return False

    def post(self, *args, **kwargs):
        try:
            pk = self.request.POST.get('pk')
        except ValueError:
            pass
        else:
            self.delete_object(pk)

        return RedirectView.post(self, *args, **kwargs)


class CalendarNoteChange(TeacherRequiredMixin, FormView):
    """Повертає html форму для зміни нотатки"""
    http_method_names = ('get', 'post', )
    template_name = 'teacher/components/calendar-note-form-modal.html'
    model = CalendarNote
    form_class = CalendarNoteForm

    def get_success_url(self):
        if hasattr(self, 'day_url'):
            return self.day_url
        return self.request.POST.get('next_to') or reverse('teacher:calendar-redirect')

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        if self.request.method == 'POST':
            pk = int(self.request.POST['pk'])
        else:
            pk = int(self.request.GET['pk'])
        kwargs['instance'] = CalendarNote.objects.get(pk=pk)
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.author != self.request.user.profile:
            return self.form_invalid(form)
        else:
            instance.save()

        # Обраховуємо посилання на день, у який ми зберігаємо цей запис
        date = form.cleaned_data['date'].timetuple()[:3]
        self.day_url = reverse('teacher:calendar-day', kwargs={'year': date[0], 'month': date[1], 'day': date[2]})
        return super(FormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['pk'] = self.request.GET.get('pk')
        return context
