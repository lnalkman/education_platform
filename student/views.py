from django.views.generic.base import TemplateView

from teacher.models import Category


# TODO: add StudentRequiredMixin
class CoursesView(TemplateView):
    template_name = 'student/courses.html'

    def get_subscribed_categories(self):
        """ Повертає масив назв категорій курсів, на які підписаний студент """
        profile = self.request.user.profile
        values_list = profile.subscribed_courses.filter(categories__name__isnull=False).values_list('categories__name').distinct()
        return [x[0] for x in values_list]

    def get_categories(self):
        return Category.objects.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(CoursesView, self).get_context_data(**kwargs)
        context['subscribed_category_names'] = self.get_subscribed_categories()
        context['categories'] = self.get_categories()
        return context
