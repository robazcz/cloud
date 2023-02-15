from django import template

register = template.Library()

@register.filter(name="indx")
def indx(item, i):
    return item[i]