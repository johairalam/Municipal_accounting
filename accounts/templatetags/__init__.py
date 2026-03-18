# accounts/templatetags/access_tags.py
from django import template
from accounts.utils import user_has_permission

register = template.Library()

@register.simple_tag(takes_context=True)
def can_access(context, code):
    user = context['request'].user
    return user_has_permission(user, code)
