from django.apps import AppConfig
from django.db.models.signals import pre_delete
from functools import partial


class TeacherConfig(AppConfig):
    name = 'teacher'
    verbose_name = 'Викладач'

    def ready(self):
        from teacher.models import LessonFile, Course
        from teacher.signals import delete_field_file

        pre_delete.connect(partial(delete_field_file, field='file'), sender=LessonFile)
        pre_delete.connect(partial(delete_field_file, field='image'), sender=Course)
