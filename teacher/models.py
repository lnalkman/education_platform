import os
import textwrap

from django.db import models
from django.shortcuts import reverse

from edu_process.models import (
    Profile, Group, profile_photo_path,
)


class Course(models.Model):
    """
    Курс включає в себе модулі, які включають заняття
    з усіма пов'язаними навчальними матеріалами.
    """
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    name = models.CharField(verbose_name='Назва курсу', max_length=128)
    description = models.TextField(verbose_name='Опис курсу', max_length=4096)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    draft = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return textwrap.shorten(self.name, width=24, placeholder='...')


class Module(models.Model):
    class Meta:
        verbose_name = 'Розділ'
        verbose_name_plural = 'Розділи'

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Назва розділу',
        max_length=128
    )
    description = models.TextField(
        verbose_name='Опис розділу',
        max_length=4096
    )
    visible = models.BooleanField(default=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (Курс: %s)' % (self.name, self.course.name)


class Lesson(models.Model):
    class Meta:
        verbose_name = 'Заняття'
        verbose_name_plural = 'Заняття'

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Назва заняття',
        max_length=255,
        blank=True,
        null=True
    )
    short_description = models.TextField(verbose_name='Короткий опис заняття', max_length=512)

    pub_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s (Курс: %s)' % (self.name, self.module.course.name)


def lesson_file_upload_path(instance, filename):
    return os.path.join(
        profile_photo_path(instance.lesson.module.course.author, ''),
        str(instance.lesson.module.course.id),
        str(instance.lesson.module.id),
        str(instance.lesson.id),
        filename
    )


class LessonFile(models.Model):
    class Meta:
        verbose_name = 'Навчальний файл'
        verbose_name_plural = 'Навчальні файли'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    file = models.FileField(verbose_name='Файл', upload_to=lesson_file_upload_path)

    def filename(self):
        full_path = self.file.name
        return full_path[full_path.rfind('/') + 1:]

    def __str__(self):
        return self.file.name


class Publication(models.Model):
    """
    Публікації викладачів. Перевірка того, що публікація викладацько повинна
    проводитьсь у views.
    """
    class Meta:
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    title = models.CharField(verbose_name='Заголовок', max_length=64)
    content = models.TextField(verbose_name='Контент', max_length=8192)
    image = models.ImageField(verbose_name='Фотокартка публікації', blank=True, null=True)

    pub_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now=True)

    def get_first_paragraph(self):
        return self.content[:self.content.find('\r\n\r\n')]

    def get_absolute_url(self):
        return reverse('teacher:blog-post', kwargs={'pk': self.pk})

    def __str__(self):
        author_user = self.author.user
        return '%(post_title)s (by: %(author)s)' % ({
            'post_title': self.title,
            'author': author_user.first_name + author_user.last_name,
        })


class CalendarNote(models.Model):
    class Meta:
        verbose_name = 'Календарний запис'
        verbose_name_plural = 'Календарні записи'

    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    title = models.CharField(verbose_name='Заголовок', max_length=48, blank=True, null=True)
    content = models.TextField(verbose_name='Нотатка', max_length=512)
    date = models.DateTimeField()

    def get_day_url(self):
        return reverse('teacher:calendar-day', kwargs={
            'year': self.date.year,
            'month': self.date.month,
            'day': self.date.day
        })

