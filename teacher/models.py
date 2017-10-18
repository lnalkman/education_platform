import os

from django.db import models

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
        return '%s (by: %s)' % (self.name, self.author.user.last_name)


class CourseLayout(models.Model):
    course = models.ForeignKey(Course)

    visible_for_all = models.BooleanField(default=True)
    visible_for_groups = models.ManyToManyField(Group)


class Module(models.Model):
    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модулі'

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Назва модулю',
        max_length=128,
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name='Опис модулю',
        max_length=4096,
        blank=True,
        null=True
    )
    visible = models.BooleanField(default=True)
    draft = models.BooleanField(default=False)
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
