from django.forms.models import ModelForm

from .models import (
    Course
)
from edu_process.models import Profile


class CourseForm(ModelForm):
    """
    Форма для створення та редагування курсів.
    Поле автора має бути визначене у відображеннях (views)
    """
    class Meta:
        model = Course
        exclude = ('author',)


class TeacherProfileForm(ModelForm):
    """
    Форма з полями, які може редагувати викладач у своєму профілі.
    """
    class Meta:
        model = Profile
        fields = (
            'about_me', 'photo',
        )
