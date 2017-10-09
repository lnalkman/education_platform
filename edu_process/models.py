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


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    course = models.PositiveSmallIntegerField(
        verbose_name='Номер курсу',
        blank=True,
        null=True
    )
    photo = models.FileField(
        verbose_name='Фото',
        blank=True,
        null=True
    )
    about_me = models.TextField(verbose_name='Інформація про студента', max_length=512)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Інформація про викладача', max_length=1024)
    photo = models.FileField(
        verbose_name='Фото',
        blank=True,
        null=True
    )


class Course(models.Model):
    """
    Курс включає в себе модулі, які включають заняття
    з усіма пов'язаними навчальними матеріалами.
    """
    description = models.TextField(verbose_name='Опис курсу', max_length=4096)
    author = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    visible = models.BooleanField(default=True)
    visible_for_groups = models.ManyToManyField(Group)

    draft = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(
        verbose_name='Опис модулю',
        max_length=4096,
        blank=True,
        null=True
    )
    visible = models.BooleanField(default=True)
    draft = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Назва заняття', max_length=255)
    short_description = models.TextField(verbose_name='Короткий опис заняття', max_length=512)

    pub_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now=True)


class LessonFile(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    file = models.FileField(verbose_name='')