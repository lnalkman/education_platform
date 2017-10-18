from django.contrib.auth import login
from django.shortcuts import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormView
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Profile


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

