from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from webapp.models import Inventory, Product

@receiver([post_save, post_delete], sender=Inventory)
def update_product_quantity(sender, instance, **kwargs):
    product = instance.product

    total = Inventory.objects.filter(
        product=product
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    product.quantity = total
    product.save()