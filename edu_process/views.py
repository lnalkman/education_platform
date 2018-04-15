import uuid

from django.core import serializers
from django.contrib.auth import login, logout
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
from django.core.files.base import ContentFile
from django.contrib import messages
from PIL import Image

from .models import Profile, Group, Message, get_user_messages
from teacher.models import Course


class IndexView(FormView):
    http_method_names = ('get', 'post',)
    template_name = 'edu_process/index.html'
    form_class = AuthenticationForm

    def get(self, request, *args, **kwargs):
        """Якщо користувач вже авторизований, то перенаправляємо його в особистий кабінет"""
        if self.request.user.is_authenticated():
            url = self.request.user.profile.get_absolute_url()
            if url:
                return HttpResponseRedirect(url)

        return super(IndexView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(IndexView, self).form_valid(form)

    def get_success_url(self):
        return self.request.user.profile.get_absolute_url()


class LogoutView(View):
    logout_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(self.logout_url)


class UserAvatarView(LoginRequiredMixin, View):
    MIN_IMAGE_SIZE = (256, 256)
    MAX_IMAGE_SIZE = (4096, 4096)
    THUMBNAIL_SIZE = (512, 512)

    def get(self):
        pass

    def get_image(self):
        """
        Отримує фотографію з post запросу. Повертає None, якщо в запросі немає фотографії.
        Генерує IOError якщо неможливо розпізнати фотогрфію
        Генерує ValueError якщо фотографія не відповідає розміру self.MIN_IMAGE_SIZE
        :return: Image object
        """
        if self.request.FILES:
            img = Image.open(self.request.FILES['photo'])

            if img.size[0] < self.MIN_IMAGE_SIZE[0] or img.size[1] < self.MIN_IMAGE_SIZE[1]:
                raise ValueError(
                    "Занадто мала фотографія. Роздільна здатність фотографії повинна бути в межах {} - {}".format(
                        self.MIN_IMAGE_SIZE,
                        self.MAX_IMAGE_SIZE
                    )
                )

            if img.size[0] > self.MAX_IMAGE_SIZE[0] or img.size[1] > self.MAX_IMAGE_SIZE[1]:
                raise ValueError(
                    "Занадто велика фотографія. Роздільна здатність фотографії повинна бути в межах {} - {}".format(
                        self.MIN_IMAGE_SIZE,
                        self.MAX_IMAGE_SIZE
                    )
                )

            return img

    def get_square_area(self, image):
        """
        Бере кординати крайніх точок діагоналі квадрата (по факту прямокутника через неточність)
        з post запросу і змінює їх у меншу сторону, щоб утворилась квадратна територія
        (з цілочисельними кориданатами).
        Генерує ValueError: якщо кординати неправильні
        Повертає квадратну територію по якій має бути обрізана фотографія
        (
            відступ зліва верхньої точки,
            відступ зверху лівої верхньої точки,
            відступ зліва нижньої правої точки,
            відступ зверху нижньої правої точки
         )
        :return: (int, int, int, int)
        """
        offset_left1 = int(float(self.request.POST.get('offset_left1', -1)))
        offset_top1 = int(float(self.request.POST.get('offset_top1', -1)))
        offset_left2 = int(float(self.request.POST.get('offset_left2', -1)))
        offset_top2 = int(float(self.request.POST.get('offset_top2', -1)))

        # Якщо кординати правої нижньої точки виходять за межі фотографії
        # зменшуємо їх до відповідних крайніх кординат фотографії
        if offset_left2 > image.size[0]:
            offset_left2 = image.size[0]

        if offset_top2 > image.size[1]:
            offset_top2 = image.size[1]

        # Перевірка чи кординати більші за 0 і права нижня точка знаходиться відповідно
        # нижче і правіше лівої верхньої точки
        if offset_left1 < 0 or offset_top1 < 0 or offset_left2 < offset_left1 or offset_top2 < offset_top1:
            raise ValueError(
                'Невірні кординати квадрату (%d, %d %d, %d)' % (offset_top1, offset_left1, offset_top2, offset_left2)
            )

        width = offset_left2 - offset_left1
        height = offset_top2 - offset_top1

        # Якщо через неточність з'явився прямокутник
        # зменшуємо більшу сторону, щоб утворився квадрат
        if height < width:
            offset_left2 -= width - height
        elif width < height:
            offset_top2 -= height - width

        return offset_left1, offset_top1, offset_left2, offset_top2

    def post(self, request, *args, **kwargs):
        if request.FILES:
            try:
                # Отримуємо об'єкт фотографії з запросу
                img = self.get_image()
            except IOError as e:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Невдалось відкрити фотографію. Можливо файл невідомого формату або пошкоджений'
                )
                messages.add_message(
                    request,
                    messages.DEBUG,
                    'DEBUG: %s' % e
                )
            except ValueError as e:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Неможливо зберегти фотографію. %s' % e
                )
            else:
                if img:
                    try:
                        # Отримуємо обрізану по області виділення фотографію
                        cropped_image = img.crop((self.get_square_area(img)))
                    except ValueError as e:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            'Невдалось зберегти фотографію. Невірно задана область виділення.'
                        )
                        messages.add_message(
                            request,
                            messages.DEBUG,
                            'DEBUG: %s' % e
                        )
                    else:
                        cropped_image.thumbnail(self.THUMBNAIL_SIZE)

                        # Прив'язуємо оброблену фотографію до профілю користувача
                        bin_img = ContentFile(b'')

                        # Рандоминий uuid, щоб браузери не кешували фотографію
                        bin_img.name = str(uuid.uuid4()) + '.' + img.format
                        cropped_image.save(bin_img, format=img.format)

                        # Прив'язуємо фотографію до користувача
                        user_profile = request.user.profile
                        user_profile.photo = bin_img
                        user_profile.save()

                        cropped_image.close()
                        img.close()

                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            'Фотографію успішно змінено'
                        )

            return HttpResponseRedirect(reverse('index'))

    def delete(self):
        pass


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


class CourseListJsonView(LoginRequiredMixin, View):
    """
    View для пошуку курсів.
    Достпупні поля:
        author_id  -> int (Курси автором яких є користувач з id профілю author_id)
        student_id -> int (Курси, на які напряму підписаний студент з id профілю student_id)
        q          -> str (Курси назва чи опис яких містить рядок пошуку q)
        offset     -> int (Скільки курсів буде пропущено при повернені списку знайдених курсів, потрібно для пагінації)
    """
    http_method_names = ('get',)

    # Максимальна кількість занять, яку повертає view
    MAX_COURSES_RETURN = 10

    def render_to_json(self, queryset):
        print(dir(queryset))
        data = {
            'queryset:': list(queryset.values()),
            'result_count': queryset.count(),
        }
        return JsonResponse(
            data,
            safe=False,
        )

    def get_queryset(self):
        queryset = Course.objects.all()
        get_data = self.request.GET

        author_id = get_data.get('author_id')
        if author_id:
            if author_id == 'self':
                queryset = queryset.filter(author__id=self.request.user.profile.id)
            else:
                queryset = queryset.filter(author__id=author_id)

        student_id = get_data.get('student_id')
        if student_id:
            if student_id == 'self':
                queryset = queryset.filter(students__id=self.request.user.profile.id)
            else:
                queryset = queryset.filter(students__id=student_id)

        # Рядок пошуку по імені і опису курсу.
        q = get_data.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        try:
            offset = int(get_data.get('offset', 0))
        except (ValueError, TypeError):
            raise ValueError('Invalid offset parameter value')

        return queryset[offset: offset + 10]

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValueError as e:
            return HttpResponseBadRequest(e)

        return self.render_to_json(
            queryset
        )
