from django.dispatch import receiver
from django.db.models.signals import post_delete
from backend.models import Booking

from django.db.models.signals import post_save


@receiver(post_delete, sender=Booking)
def delete_booking_signal(sender, instance, **kwargs):
    # Update available places when booking is deleted.
    instance.calc_available()


@receiver(post_save, sender=Booking)
def notify_booking_update(sender, instance, **kwargs):
    """Trigger SSE updates when a booking is saved."""
    print(f"Booking {instance.id} status updated to {instance.status.description}")




