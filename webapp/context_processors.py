from django.db import models
from .models import Menu

def dynamic_menu(request):
    if not request.user.is_authenticated:
        return {'menus': []}

    user = request.user
    user_groups = user.groups.all()

    # SUPERUSER sees everything
    if user.is_superuser:
        menus = Menu.objects.filter(parent__isnull=True).order_by('order')
    else:
        menus = Menu.objects.filter(
            parent__isnull=True
        ).filter(
            models.Q(groups__in=user_groups) | models.Q(groups__isnull=True)
        ).distinct().order_by('order')
    
    menus = Menu.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related("children__children").order_by("order")
    

    return {'menus': menus}