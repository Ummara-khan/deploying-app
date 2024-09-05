from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SanctionRecord

@receiver(post_save, sender=SanctionRecord)
def create_variations(sender, instance, created, **kwargs):
    if created:
        # Call the generate_variations method to create variations
        instance.generate_variations()
