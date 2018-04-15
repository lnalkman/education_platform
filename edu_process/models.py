import os

from django.contrib.auth.models import User
from django.db import models, connection
from django.core.exceptions import ObjectDoesNotExist


class Group(models.Model):
    """
    Збирає студентів у групи.
    """
    name = models.CharField(
        verbose_name='Назва групи',
        max_length=12,
        blank=True,
        null=True
    )
    courses = models.ManyToManyField(
        'teacher.Course',
        blank=True
    )

    def __str__(self):
        return self.name


def profile_photo_path(instance, filename):
    return os.path.join(instance.user_type, instance.user.username, filename)


class Profile(models.Model):
    """
    Профіль студента і викладача в одній моделі, тип задається
    полем user_type, кожен тип може мати специфічні поля, які
    потірбно ховати від іншого типу користувача (поля для студента
    потрібно ховати при роботі з викладачем).
    """
    TEACHER = 'TC'
    STUDENT = 'ST'
    USER_TYPES = (
        (TEACHER, 'Викладач'),
        (STUDENT, 'Студент'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        verbose_name='Тип користувача',
        max_length=4,
        choices=USER_TYPES,
        default=STUDENT
    )

    # Специфічні поля для студента
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    photo = models.FileField(
        verbose_name='Фото',
        upload_to=profile_photo_path,
        blank=True,
        null=True
    )
    about_me = models.TextField(
        verbose_name='Інформація про мене',
        max_length=512,
        blank=True,
        null=True
    )

    def is_teacher(self):
        return self.user_type == self.TEACHER

    def is_student(self):
        return self.user_type == self.STUDENT

    def save(self, *args, **kwargs):
        try:
            # Підніме виключення, якщо цей об'єкт не збережено в БД
            curr_photo = Profile.objects.get(pk=self.pk).photo

            # Видаляємо стару фотографію
            if curr_photo != self.photo:
                curr_photo.delete(save=False)

            # Якщо користувач став активним, видяляємо об'єкт тимчасового користувача
            # який зв'язаний з цим профілем.
            if self.user.is_active and not Profile.objects.get(pk=self.pk).user.is_active:
                try:
                    self.temp_user.delete()
                except User.DoesNotExist:
                    pass
        # Помилка виникає, якщо об'єкт створюється(не оновлюється)
        except ObjectDoesNotExist:
            pass

        # Зберігаємо нову фотографію
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s (%s)' % (self.user.first_name,
                               self.user.last_name,
                               self.get_user_type_display()
                               )


class TemporaryUser(models.Model):
    """
    Модель тимчасового користувача, ссилається на користувачів
    з атрибутом is_active == False.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='temp_user',
        null=True,
        )
    password = models.CharField(verbose_name='Тимчасовий пароль', max_length=32)


class Message(models.Model):
    class Meta:
        ordering = ('-id',)

    sender = models.ForeignKey(User, related_name='sended_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)

    text = models.TextField(verbose_name='Текст повідомлення', max_length=512)
    sended = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:36]


def get_user_messages(id):
    """
    Повертає масив словників з усіма користувачами з якими спілкувався користувач з id
    Структура queryset:
    1) au.id id,
    2) msg.text text,
    3) msg.who who [вам прислали повідомлення чи ви відіслали],
    4) msg.sended sended,
    5) au.first_name first_name,
    6) au.last_name last_name
    7) epp.photo photo
    """

    with connection.cursor() as cursor:
        cursor.execute("""
        select
        au.id id,
        msg.text message,
        msg.who who,
        msg.sended sended,
        au.first_name first_name,
        au.last_name last_name,
        epp.photo image
        FROM (
          SELECT
            id,
            text,
            CASE WHEN receiver_id = %(id)s
              THEN sender_id
            WHEN sender_id = %(id)s
              THEN receiver_id END AS user,
            CASE WHEN receiver_id = %(id)s
              THEN 'from'
            WHEN sender_id = %(id)s
              THEN 'you' END      AS who,
            sended
          FROM edu_process_message epm
          WHERE (receiver_id = %(id)s OR sender_id = %(id)s)
                AND id IN
                    (SELECT max(id)
                     FROM (SELECT
                             id,
                             CASE WHEN receiver_id = %(id)s
                               THEN sender_id
                             WHEN sender_id = %(id)s
                               THEN receiver_id END AS user
                           FROM edu_process_message epm
                           WHERE (receiver_id = %(id)s OR sender_id = %(id)s)
                          ) t
                     GROUP BY user
                    )
        ) msg
        inner join auth_user au on msg.user = au.id
        inner join edu_process_profile epp on au.id = epp.user_id
        order by msg.id desc""" % ({'id': id}))

        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]