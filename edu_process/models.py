from django.contrib.auth.models import User
from django.db import models


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

    def __str__(self):
        return '%s %s (%s)' % (self.user.first_name,
                               self.user.last_name,
                               self.get_user_type_display()
                               )
