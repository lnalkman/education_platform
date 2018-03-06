from django.core import serializers
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.http.response import (
    HttpResponseRedirect, HttpResponse, JsonResponse,
    HttpResponseBadRequest, HttpResponseNotFound
)
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView

from .models import Profile, Group, Message, get_user_messages


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


class MessageView(LoginRequiredMixin, TemplateView):
    template_name = 'edu_process/messages.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['self_id'] = self.request.user.pk
        return context


class MessagesApiView(LoginRequiredMixin, View):

    def get_messages(self, user_pk, last_message_pk=None, count=15):
        if count > 30 or count < 1:
            count = 15

        if last_message_pk and last_message_pk < 0:
            last_message_pk = 0

        user1 = self.request.user
        try:
            user2 = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return []

        if not last_message_pk:
            # Повідомлення між користувачами
            msg_condition = (Q(sender=user1) & Q(receiver=user2)) | (Q(sender=user2) & Q(receiver=user1))
        else:
            # Повідомлення між користувачами pk яких менше за last_message_pk
            msg_condition = (
                Q(id__lt=last_message_pk)
                & ((Q(sender=user1) & Q(receiver=user2)) | (Q(sender=user2) & Q(receiver=user1)))
            )

        return Message.objects.filter(msg_condition)[:count]

    def render_to_json(self, queryset):
        return HttpResponse(
            serializers.serialize('json', queryset),
            content_type='application/json'
        )

    def get(self, request, *args, **kwargs):
        try:
            last_message_pk = int(request.GET.get('last_message_pk', 0))
            count = int(request.GET.get('count', 15))
            user_pk = int(request.GET.get('id'))
        except TypeError:
            return HttpResponseBadRequest("last_message_pk, count, user_pk variables should be integer digits")

        queryset = self.get_messages(user_pk, last_message_pk, count)
        return self.render_to_json(queryset)

    def post(self, request, *args, **kwargs):
        try:
            receiver_pk = int(request.POST.get('receiver_pk'))
        except ValueError:
            return HttpResponseBadRequest("user_pk variable should be integer digit")
        message = request.POST.get('message')
        if not message:
            return HttpResponseBadRequest("message can't be empty")

        try:
            receiver = User.objects.get(pk=receiver_pk)
        except User.DoesNotExist:
            return HttpResponseNotFound("user with pk=%s doesn't exists" % receiver_pk)

        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            text=message
        )

        return HttpResponse(msg.sended)


class MessageUserApiView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def render_to_json(self, queryset):
        return JsonResponse(
            queryset,
            safe=False,
        )

    def get_queryset(self, id):
        return get_user_messages(id)

    def get(self, request, *args, **kwargs):
        id = request.user.pk

        queryset = self.get_queryset(id)
        return self.render_to_json(queryset)
