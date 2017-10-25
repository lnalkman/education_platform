import string
import random
from functools import partial

from django.forms import models, widgets
from django.contrib.auth.models import User

from edu_process.models import TemporaryUser

PASSWORD_CHOICES = string.ascii_lowercase + string.digits


def random_password(length=6):
    """Повертає строку довжиною length з випадковим розташуванням цифр та маленьких букв ascii """
    return ''.join(random.choice(PASSWORD_CHOICES) for i in range(length))


class TempUserForm(models.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')
        widgets = {
            'username': widgets.TextInput(attrs={'class': 'form-control'}),
            'first_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'last_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'password': widgets.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, *args, **kwargs):
        """Зберігає тимчасового користувача в БД"""
        user = super(TempUserForm, self).save(*args, **kwargs)
        TemporaryUser(user, self.password).save()
        return user

