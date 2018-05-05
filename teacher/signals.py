def delete_field_file(sender, instance, using, field, **kwargs):
    # Видаляємо файл зв'язаний об'єктом класу LessonFile
    instance.getattr(field).delete(save=False)
