from django import forms
from django.forms.models import ModelForm

from .models import (
    Course, CalendarNote, Module
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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
        }


class ModuleForm(ModelForm):
    """Форма для створення та редагування модулів"""
    class Meta:
        model = Module
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
            'course': forms.HiddenInput()
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
    class Meta:
        model = CalendarNote
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'cols': 9}),
            'lesson': forms.Select(attrs={'class': 'form-control', 'hidden': '1'}),
            'date': forms.TextInput(attrs={'class': 'form-control'}),
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
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
