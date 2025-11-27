
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserWallet, Transaction


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        # Only create wallet if it doesn't exist
        if not hasattr(instance, 'wallet'):
            # Create wallet with 0 initial credits
            wallet = UserWallet.objects.create(user=instance, credits=0)
            # Add the welcome bonus credits and create the transaction
            wallet.add_credits(10, description="Welcome bonus - A gift from a pigeon")
