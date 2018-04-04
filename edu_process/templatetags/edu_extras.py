import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# 3 або більше відступи а також пробіли після них
REG_EXP = re.compile(r'([\n]+\s*){3,}')


@register.filter
@stringfilter
def cut_extra_indent(value):
    return re.sub(REG_EXP, '\n\n', value)