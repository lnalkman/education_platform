from django.db.models.query import QuerySet


class AbstractAjaxAction:
    """
    :code - код дії C{string}
    :verbose_name - назва дії
    :prompt - чи потребує дія підтвердження
    :using_queryset - чи потребує ця дія queryset
    """
    code = None
    verbose_name = None
    prompt = False
    using_queryset = True

    def get_prompt_text(self):
        """
        :return: Текст запиту C{string}
        """
        if hasattr(self, 'prompt_text'):
            return self.prompt_text
        return ''

    def get_answer_variants(self):
        """
        :return: словник з ключами - варіантами відповіді і значеннями - з докладним ім'ям відповіді
        ключі повинні мати назви відповідних методів, які будуть виконувати цю дію.
        """
        if hasattr(self, 'answer_variants'):
            return self.answer_variants
        return {'yes': 'Yes'}


class AjaxAction(AbstractAjaxAction):
    def __init__(self, queryset=None, answers=None):
        if self.using_queryset and answers:
            if not isinstance(queryset, QuerySet):
                raise ValueError(
                    'queryset should be defined as QuerySet class or subclass object.'
                    'Set using_queryset attribute False if action don\'t use queryset'
                )
            self.queryset = queryset
        else:
            self.queryset = None

        if self.prompt and answers:
            self.confirmed = True

        self.answers = answers

    def do_actions(self):
        for answer in self.answers:
            if hasattr(self, answer):
                getattr(self, answer)()


class DeleteAction(AbstractAjaxAction):
    code = 'delete'
    verbose_name = 'Видалити обраних користувачів'
    prompt = True
    prompt_text = 'Ви справді хочете видалити обраних користувачів'

    def __init__(self, queryset=None):
        self.queryset = queryset

    def yes(self):
        self.queryset.delete()
