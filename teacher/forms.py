from django import forms
from django.forms.models import ModelForm

from .models import (
    Course, CalendarNote, Module,
    Lesson, Publication
)
from edu_process.models import Profile


class CourseForm(ModelForm):
    """
    Форма для створення та редагування курсів.
    Поле автора має бути визначене у відображеннях (views)
    """

    class Meta:
        model = Course
        exclude = ('students', 'author')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class ModuleForm(ModelForm):
    """Форма для створення та редагування розділів"""

    class Meta:
        model = Module
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
            'course': forms.HiddenInput()
        }


class LessonForm(ModelForm):
    """Форма для створення та редагування уроків"""

    class Meta:
        model = Lesson
        fields = ('name', 'short_description',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 9}),
        }


class TeacherProfileForm(ModelForm):
    """
    Форма з полями, які може редагувати викладач у своєму профілі.
    """

    class Meta:
        model = Profile
        fields = (
            'about_me', 'photo',
        )


class CalendarNoteForm(ModelForm):
    date = forms.DateTimeField(
        input_formats=('%Y-%m-%dT%H:%M',),
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format="%Y-%m-%dT%H:%M"
        ))

    class Meta:
        model = CalendarNote
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': ''}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
            'lesson': forms.Select(attrs={'class': 'form-control', 'hidden': '1', 'required': ''}),
            'author': forms.HiddenInput(),
        }

    def __init__(self, *args, date=None, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        author = self.initial['author'] if self.initial else self.instance.author
        self.fields['course'] = forms.ModelChoiceField(
            queryset=Course.objects.filter(author=author),
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        if not self.is_bound and date:
            self.fields['date'] = forms.DateTimeField(
                initial=date,
                input_formats=('%Y-%m-%dT%H:%M',),
                widget=forms.DateTimeInput(
                    attrs={'class': 'form-control', 'type': 'datetime-local'},
                    format="%Y-%m-%dT%H:%M"
                ))


class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        exclude = ('author',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': ''}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'cols': 6}),
        }

    @classmethod
    def make_thumbnail(cls, image):
        """
        TODO: Метод має зменшувати фотографію, та повертати її.
        Застосувати його в методі save форми.
        :param image: PIL.Image object
        :return: PIL.Image object -> зменшена фотографія
        """
        pass
