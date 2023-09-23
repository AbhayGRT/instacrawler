from django import template

register = template.Library()

@register.filter
def enumerate_angles(angles):
    return enumerate(angles)
