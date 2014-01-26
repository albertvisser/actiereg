from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

#~ @register.filter
#~ @stringfilter
#~ def nbrk(value):
    #~ "Make all spaces nonbreaking"
    #~ return value.replace(' ', '&nbsp;')
#~ nbrk.is_safe = True

@register.filter
@stringfilter
def trimat(text,leng,autoescape=None):
    "Display up to a certain length"
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    if len(text) > leng:
        text = text[:leng] + "..."
    return mark_safe(esc(text))
trimat.needs_autoescape = False
trimat.is_safe = True

#~ def initial_letter_filter(text, autoescape=None):
    #~ first, other = text[0], text[1:]
    #~ if autoescape:
        #~ esc = conditional_escape
    #~ else:
        #~ esc = lambda x: x
    #~ result = '<strong>%s</strong>%s' % (esc(first), esc(other))
    #~ return mark_safe(result)
#~ initial_letter_filter.needs_autoescape = True
