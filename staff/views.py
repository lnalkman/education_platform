from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import JsonResponse

from .forms import TempUserForm


class StaffRequired(LoginRequiredMixin ,UserPassesTestMixin):
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_staff


class TeacherAdmin(StaffRequired, FormView):
    template_name = 'staff/teacher_page.html'
    form_class = TempUserForm

    def form_valid(self, form):
        return JsonResponse({
            'text': '<strong>Успіх!</strong>'
                    '<br>Викладач <strong>%(full_name)s</strong> <br>'
                    'Тимчасовий пароль: %(password)s' % (
                {
                    'full_name': form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name'],
                    'password': form.cleaned_data['password'],
                }
            ),
            'status': '200'})

    def form_invalid(self, form):
        return JsonResponse({
            'text': '<strong>Помилка!</strong>'
                    '<br>Не вдалось створити профіль. Перевірте введені данні та спробуйте ще раз',
            'status': '400',
            'errors': form.errors.as_json(),
        })

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(profile__user_type='TC')
        context['inactive_user_list'] = User.objects.filter(is_active=False)
        return context
