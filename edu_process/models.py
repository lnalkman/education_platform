import os

from django.contrib.auth.models import User
from django.db import models
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
    course_number = models.PositiveSmallIntegerField(
        verbose_name='Номер курсу',
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