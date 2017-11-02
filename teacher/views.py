from calendar import HTMLCalendar
from datetime import datetime
from functools import partial

from django.urls import reverse_lazy
from django.shortcuts import reverse
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.base import TemplateView


from .models import Course, CalendarNote
from .forms import CourseForm, TeacherProfileForm


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

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
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


class HrefCalendar(HTMLCalendar):

    # Якщо в цей день є якісь події/нотатки
    booked_class = 'booked'

    href = '#'

    def __init__(self, theyear, themonth, booked_days=None):
        """:booked_days -> контейнер в якому зберігаються дні в місяці в яких є якісь нотатки"""
        HTMLCalendar.__init__(self)
        self.theyear = theyear
        self.themonth = themonth
        self.booked_days = booked_days
        # self.href = partial(reverse, year=theyear, month=)

    def formatday(self, day, weekday, booked=False):

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s %s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday],
                                                                   self.booked_class if booked else '',
                                                                   self.href,
                                                                   day
                                                                   )

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, d in self.booked_days) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(self.theyear, self.themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(self.theyear, self.themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class CalendarView(TemplateView):
    template_name = 'teacher/calendar.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['curr_year'], context['curr_month'] = datetime.now().timetuple()[:2]
        booked_days = [
            day for day in CalendarNote.objects.filter(date__year=int(kwargs['year']), date__month=int(kwargs['month']))
        ]
        context['calendar_table'] = HrefCalendar(theyear=int(kwargs['year']),
                                                 themonth=int(kwargs['month']),
                                                 booked_days=booked_days,
                                                 ).formatmonth()
        return context
