from django.db import models
from edu_process.models import Profile, Group


class Course(models.Model):
    """
    Курс включає в себе модулі, які включають заняття
    з усіма пов'язаними навчальними матеріалами.
    """
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курси'

    description = models.TextField(verbose_name='Опис курсу', max_length=4096)
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    visible = models.BooleanField(default=True)
    visible_for_groups = models.ManyToManyField(Group)

    draft = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)


class Module(models.Model):
    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модулі'

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
    class Meta:
        verbose_name = 'Заняття'
        verbose_name_plural = 'Заняття'

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Назва заняття', max_length=255)
    short_description = models.TextField(verbose_name='Короткий опис заняття', max_length=512)

    pub_date = models.DateTimeField(auto_now_add=True)
    change_date = models.DateTimeField(auto_now=True)


class LessonFile(models.Model):
    class Meta:
        verbose_name = 'Навчальний файл'
        verbose_name_plural = 'Навчальні файли'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    file = models.FileField(verbose_name='')
