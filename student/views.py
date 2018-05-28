from datetime import datetime

from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import reverse
from django.views.generic.base import RedirectView
from django.http.response import HttpResponseRedirect
from django.contrib import messages

import teacher
from teacher.models import Category, CalendarNote
from edu_process.models import Profile, Message


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Надає доступ до сторінки тільки студентам"""
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.profile.is_student()


class StudentAccountView(LoginRequiredMixin, DetailView):
    model = Profile

    account_owner_template_name = 'student/student-account.html'
    review_account_template_name = 'student/student-account-review.html'

    def user_account_owner(self):
        """ Перевіряє чи належить профіль сторінки на яку зайшли тому, хто зайшов на неї """
        return self.request.user.profile.pk == int(self.kwargs['pk'])

    def get_template_names(self):
        if self.user_account_owner():
            return self.account_owner_template_name
        return self.review_account_template_name

    def get_student_courses(self):
        return self.object.subscribed_courses.all()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        message = request.POST.get('message')
        if message:
            from_ = self.request.user
            to = self.object.user

            Message.objects.create(sender=from_, receiver=to, text=message)
            messages.add_message(
                request,
                messages.SUCCESS,
                'Повідомлення надіслано'
            )

        return HttpResponseRedirect(self.object.get_absolute_url())




class CoursesView(StudentRequiredMixin, TemplateView):
    template_name = 'student/courses.html'

    def get_subscribed_categories(self):
        """ Повертає масив назв категорій курсів, на які підписаний студент """
        profile = self.request.user.profile
        values_list = Category.objects.filter(course__in=profile.subscribed_courses.all()).distinct()
        return values_list

    def get_categories(self):
        return Category.objects.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(CoursesView, self).get_context_data(**kwargs)
        context['subscribed_categories'] = self.get_subscribed_categories()
        context['categories'] = self.get_categories()
        return context


class CalendarView(StudentRequiredMixin, TemplateView):
    http_method_names = ('get',)
    template_name = 'student/calendar.html'

    def get(self, *args, **kwargs):
        try:
            year, month = int(kwargs.get('year', 0)), int(kwargs.get('month', 0))
            if not (isinstance(year, int) and isinstance(month, int)
                    and 1995 < year < 2500 and 0 < month <= 12):
                raise ValueError('Invalid year or month value.')
        except ValueError:
            return HttpResponseRedirect(reverse('student:calendar-redirect'))
        return TemplateView.get(self, *args, **kwargs)

    def get_booked_days(self, year, month):
        """Повертає множину днів заданого року та місяця у яких є події цього студента"""
        return {q.date.day for q in CalendarNote.objects.filter(
            course__in=self.request.user.profile.subscribed_courses.all(),
            date__year=year,
            date__month=month
        )}

    def get_prev_month_url(self, year, month):
        """Повертає посилання не попередній місяць"""
        if month == 1:
            return reverse('student:calendar', kwargs={'year': year - 1, 'month': 12})
        return reverse('student:calendar', kwargs={'year': year, 'month': month - 1})

    def get_next_month_url(self, year, month):
        """Повертає посилання не наступний місяць"""
        if month == 12:
            return reverse('student:calendar', kwargs={'year': year + 1, 'month': 1})
        return reverse('student:calendar', kwargs={'year': year, 'month': month + 1})

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['curr_year'], context['curr_month'] = datetime.now().timetuple()[:2]
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        context['year'], context['month'] = year, month
        context['prev_month_url'] = self.get_prev_month_url(year, month)
        context['next_month_url'] = self.get_next_month_url(year, month)

        booked_days = self.get_booked_days(year, month)
        context['calendar_table'] = teacher.views.HrefCalendar(
            theyear=year,
            themonth=month,
            day_url_name='student:calendar-day',
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
        return reverse('student:calendar', kwargs={'year': year, 'month': month})


class CalendarDayView(StudentRequiredMixin, ListView):
    template_name = 'student/calendar-day.html'

    def get_queryset(self):
        return CalendarNote.objects.filter(
            course__in=self.request.user.profile.subscribed_courses.all(),
            date__year=self.kwargs['year'],
            date__month=self.kwargs['month'],
            date__day=self.kwargs['day']
        )

    def get_context_data(self, **kwargs):
        context = super(CalendarDayView, self).get_context_data(**kwargs)
        context['month_url'] = reverse('student:calendar', kwargs={
            'year': self.kwargs['year'],
            'month': self.kwargs['month']
        })
        context['day_date'] = datetime(
            int(self.kwargs['year']),
            int(self.kwargs['month']),
            int(self.kwargs['day']),
        )
        context['day_url'] = reverse(
            'student:calendar-day',
            kwargs={
                'year': self.kwargs['year'],
                'month': self.kwargs['month'],
                'day': self.kwargs['day']
            }
        )

        return context
