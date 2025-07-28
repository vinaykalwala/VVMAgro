from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Inventory.models import Product  # replace with your model
from Inventory.utils.logger import log_action

@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    user = getattr(instance, 'modified_by', 'System')
    action = "Created" if created else "Updated"
    log_action(user, action, 'Product', instance.id)

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    user = getattr(instance, 'modified_by', 'System')
    log_action(user, 'Deleted', 'Product', instance.id)
