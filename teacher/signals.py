def delete_lesson_file(sender, instance, using, **kwargs):
    # Видаляємо файл зв'язаний об'єктом класу LessonFile
    instance.file.delete(save=False)
