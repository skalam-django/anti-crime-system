from django import template
from django.conf import settings
from django.urls import reverse

from notipush.utils import get_templatetag_context

register = template.Library()


@register.filter
@register.inclusion_tag('notipush_header.html', takes_context=True)
def notipush_header(context):
    template_context = get_templatetag_context(context)
    return template_context


@register.filter
@register.inclusion_tag('notipush_button.html', takes_context=True)
def notipush_button(context):
    template_context = get_templatetag_context(context)
    return template_context
