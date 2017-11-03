from calendar import HTMLCalendar
from calendar import month_name
from datetime import datetime
from functools import partial

from django.urls import reverse_lazy
from django.shortcuts import reverse
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.base import TemplateView, RedirectView
from django.http.response import HttpResponseRedirect

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

    def __init__(self, theyear, themonth, prew_url='#', next_url='#', booked_days=None):
        """:booked_days -> контейнер в якому зберігаються дні в місяці в яких є якісь нотатки"""
        HTMLCalendar.__init__(self)
        self.theyear = theyear
        self.themonth = themonth
        self.prew_url = prew_url
        self.next_url = next_url
        self.booked_days = booked_days
        # self.href = partial(reverse, year=theyear, month=)

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
                                                                   self.href,
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
            year, month = self.request.GET.get('year', 0), self.request.GET.get('month', 0)
            if not (isinstance(year, int) and isinstance(month, int)
                and 1995 < year < 2500 and 0 < month <= 12):
                year, month = datetime.now().timetuple()[:2]
        else:
            year, month = datetime.now().timetuple()[:2]
        return reverse('teacher:calendar', kwargs={'year': year, 'month': month})
