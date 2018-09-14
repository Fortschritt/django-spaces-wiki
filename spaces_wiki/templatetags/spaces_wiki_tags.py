from django import template
from collab.util import is_owner_or_admin

register = template.Library()

@register.simple_tag
def hidden_if_not_owner(user, obj, space):
    """
    Returns "disabled" if user is not allowed to modify/delete a post, else ''.
    Useful for disabling dom elements.

    Usage:
    {% disabled_if_not_owner user file space %}
    """
    return '' if is_owner_or_admin(user, obj.owner, space) else 'display:none;'


