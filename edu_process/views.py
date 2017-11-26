from django.core import serializers
from django.contrib.auth import login
from django.shortcuts import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy

from .models import Profile, Group


class IndexView(FormView):
    http_method_names = ('get', 'post',)
    template_name = 'edu_process/index.html'
    form_class = AuthenticationForm
    user_type_urls = {
        Profile.TEACHER: reverse_lazy('teacher:index'),
        Profile.STUDENT: reverse_lazy('student-profile'),
    }

    def get(self, request, *args, **kwargs):
        """Якщо користувач вже авторизований, то перенаправляємо його в особистий кабінет"""
        if self.request.user.is_authenticated():
            # Отримуємо адресу на особистий кабінет
            url = self.user_type_urls.get(
                self.request.user.profile.user_type,
                None
            )
            if url:
                return HttpResponseRedirect(url)
        return super(FormView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(FormView, self).form_valid(form)

    def get_success_url(self):
        user_type = self.request.user.profile.user_type
        if user_type == Profile.TEACHER:
            return reverse('teacher:index')
        elif user_type == Profile.STUDENT:
            return reverse('student-profile')


class SearchGroup(View):
    http_method_names = ('get',)
    model = Group
    # Стандартна кількість записів, які повертає view
    returned_object_count = 5
    # Максимальна кількість записів, яку може повернути view
    limit_returned_objects = 15

    def render_to_json(self, queryset=None):
        json = serializers.serialize('json', queryset, fields=('name',))
        return HttpResponse(json, content_type='application/json')

    def get_objects(self, q, val=None):
        queryset = self.model.objects.filter(name__icontains=q)
        if val:
            return queryset[:val]
        return queryset

    def get(self, request, *args, **kwargs):
        # Строка пошуку
        q = request.GET.get('q')

        # Кількість резульатів, які протрібно повернути
        try:
            val = int(request.GET.get('val', -1))
            if val not in range(1, self.limit_returned_objects + 1):
                raise ValueError
        except ValueError:
            val = self.returned_object_count

        queryset = self.get_objects(q, val)
        return self.render_to_json(queryset)