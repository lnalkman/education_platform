from django.apps import AppConfig
from django.db.models.signals import pre_delete


class TeacherConfig(AppConfig):
    name = 'teacher'
    verbose_name = 'Викладач'

    def ready(self):
        from teacher.models import LessonFile
        from teacher.signals import delete_lesson_file
        pre_delete.connect(delete_lesson_file, sender=LessonFile)
