from django.contrib import admin
from .models import (
    Course, Module, Lesson,
    LessonFile,
)

admin.site.register((
    Course, Module, Lesson,
    LessonFile
))
