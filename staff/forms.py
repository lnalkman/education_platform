from django.forms import models
from django.contrib.auth.models import User
from django.forms.fields import SlugField

from edu_process.models import TemporaryUser, Profile


class TempUserForm(models.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')
        field_classes = {'username': SlugField}

    def __init__(self, *args, **kwargs):
        super(models.ModelForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, *args, **kwargs):
        """Зберігає тимчасового користувача в БД"""
        # Створюємо звичайного неактивного користувача за данними форми
        user = super(TempUserForm, self).save(commit=False, *args, **kwargs)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False
        user.save()

        # Прив'язуємо новоствореного користувача до профілю викладача
        profile = Profile(user=user, user_type=Profile.TEACHER)
        profile.save()

        # Прив'язуємо профіль до тимчасового користувача.
        TemporaryUser(profile=profile, password=self.cleaned_data['password']).save()
        return user

