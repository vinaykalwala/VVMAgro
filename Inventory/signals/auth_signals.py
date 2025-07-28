from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from Inventory.utils.logger import log_action

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    log_action(user, "Login", "User")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    log_action(user, "Logout", "User")
