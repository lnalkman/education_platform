from django.views.generic.base import TemplateView

from teacher.models import Category


# TODO: add StudentRequiredMixin
class CoursesView(TemplateView):
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
