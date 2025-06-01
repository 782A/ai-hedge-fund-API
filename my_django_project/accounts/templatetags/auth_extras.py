# accounts/templatetags/auth_extras.py
from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    # This check ensures we don't try to access .groups on an anonymous user
    if not user.is_authenticated:
        return False
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False
