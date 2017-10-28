from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.db.models import Q

from .forms import TempUserForm


class StaffRequired(LoginRequiredMixin ,UserPassesTestMixin):
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_staff


class TeacherAdmin(StaffRequired, FormView):
    template_name = 'staff/teacher_page.html'
    form_class = TempUserForm

    def form_valid(self, form):
        form.save()
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

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            if self.request.GET.get('q') == 'inactive_users':
                search_val = self.request.GET.get('search')
                if search_val:
                    context = {
                        'inactive_user_list': User.objects.filter(
                            Q(is_active=False),
                            Q(first_name__contains=search_val) | Q(last_name__contains=search_val)
                        )
                    }
                else:
                    context = {'inactive_user_list': User.objects.filter(is_active=False)}
                return TemplateResponse(
                    self.request,
                    template='staff/tables/inactive-teacher-list.html',
                    context=context

                )
            return HttpResponseForbidden('Invalid q value.')

        return super(FormView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(profile__user_type='TC', is_active=True)
        context['inactive_user_list'] = User.objects.filter(is_active=False)
        return context
