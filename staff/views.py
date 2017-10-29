from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponseForbidden, HttpResponse
from django.db.models import Q

from .forms import TempUserForm
from .admin import DeleteAction


class StaffRequired(LoginRequiredMixin ,UserPassesTestMixin):
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_staff


class TeacherAdmin(StaffRequired, FormView):
    """
    View генерує сторінку з таблицями викладачів(активні/неактивні)
    Обробляє форму додавання нового викладача
    """
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

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(profile__user_type='TC', is_active=True)
        context['inactive_user_list'] = User.objects.filter(profile__user_type='TC', is_active=False)
        context['delete_action'] = DeleteAction()
        return context


class AjaxTeacherAdmin(StaffRequired, TemplateView):
    """
    Повертає данні таблиці користувачів.
    page_kwargs:
    :is_active - повертати активних/неактивних користувачів(якщо задано - поверне активних)
    :q - строка пошуку (пошук по іменам та фаміліям)
    """
    http_method_names = ['get', 'post']

    def post(self, *args):
        action_code = self.request.POST.get('action')
        if action_code == DeleteAction.code:
            ids = self.request.POST.getlist('user_pk')
            DeleteAction(User.objects.filter(is_active=False, profile__user_type='TC', id__in=ids)).yes()
        return HttpResponse()

    def get_template_names(self):
        if bool(self.request.GET.get('is_active')):
            return ('staff/tables/teacher-list.html',)
        return ('staff/tables/inactive-teacher-list.html',)

    def get_context_name(self):
        if bool(self.request.GET.get('is_active')):
            return 'user_list'
        return 'inactive_user_list'

    def get_queryset(self):
        is_active = bool(self.request.GET.get('is_active'))
        search_val = self.request.GET.get('q')

        if search_val:
            return User.objects.filter(
                Q(is_active=is_active),
                Q(first_name__icontains=search_val) | Q(last_name__icontains=search_val)
            )
        return User.objects.filter(is_active=is_active)

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context[self.get_context_name()] = self.get_queryset()
        return context
