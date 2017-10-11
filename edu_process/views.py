from django.contrib.auth import login
from django.shortcuts import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormView

from .models import Profile


class IndexView(FormView):
    http_method_names = ('get', 'post',)
    template_name = 'edu_process/index.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(FormView, self).form_valid(form)

    def get_success_url(self):
        user_type = self.request.user.profile.user_type
        if user_type == Profile.TEACHER:
            return reverse('teacher:index')
        elif user_type == Profile.STUDENT:
            return reverse('student-profile')

    def render_to_response(self, context, **response_kwargs):
        """
        Додаємо до контексту посилання на особистий кабінет, якщо
        користувач вже авторизований.
        """
        user = self.request.user
        if user.is_authenticated:
            context['authenticated'] = True
            context['profile_url'] = self.get_success_url()
        else:
            context['authenticated'] = False
        return super(FormView, self).render_to_response(context, **response_kwargs)
