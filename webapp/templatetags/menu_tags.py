from django import template

from django import template

register = template.Library()

@register.inclusion_tag('webapp/menu_recursive.html', takes_context=True)
def render_menu(context, menus):
    user = context['request'].user
    return {
        'menus': menus,
        'user': user,   # pass user to template
    }


# Safe filter to check if user is in menu's groups
@register.filter
def has_group(user, groups):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return user.groups.filter(id__in=groups.values_list('id', flat=True)).exists()
    return user.groups.filter(id__in=groups.values_list('id', flat=True)).exists()