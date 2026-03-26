from functools import wraps
from django.shortcuts import redirect
from webapp.models import Menu

# webapp/utils.py
def get_user_content_types(user):
    return (
        user.user_permissions
        .select_related("content_type")
        .values(
            "content_type__app_label",
            "content_type__model",
        )
        .distinct()
    )

def group_required_for_menu(menu_name, login_url='login'):
    """
    Decorator to restrict access to a view based on the groups
    assigned to a Menu item in the Menu table.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)

            user_groups = request.user.groups.all()

            try:
                menu = Menu.objects.get(name=menu_name)
            except Menu.DoesNotExist:
                # Deny access if menu not found
                return redirect(login_url)

            # Check if menu has groups, and if user is in one of them
            if menu.groups.exists():
                allowed_group_ids = menu.groups.values_list('id', flat=True)
                if not user_groups.filter(id__in=allowed_group_ids).exists():
                    return redirect(login_url)

            # Access allowed
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator