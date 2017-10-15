from django.forms.models import ModelForm

from .models import (
    Course
)


class CourseForm(ModelForm):
    """
    Форма для створення та редагування курсів.
    Поле автора має бути визначене у відображеннях (views)
    """
    class Meta:
        model = Course
        exclude = ('author',)
