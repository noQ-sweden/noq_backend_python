from django.dispatch import receiver
from django.db.models.signals import post_delete
from backend.models import Booking
from django.core.cache import cache
from django.db.models.signals import post_save


@receiver(post_delete, sender=Booking)
def delete_booking_signal(sender, instance, **kwargs):
    # Update available places when booking is deleted.
    instance.calc_available()


@receiver(post_save, sender=Booking)
def notify_booking_update(sender, instance, **kwargs):
    """Signal fires when a booking's status changes, stores the update in cache."""
    cache_key = f"booking_update_{instance.id}"
    updated_booking = {
        "id": instance.id,
        "status": instance.status.description,
        "user": f"{instance.user.first_name} {instance.user.last_name}",
        "start_date": instance.start_date.strftime("%Y-%m-%d"),
        "end_date": instance.end_date.strftime("%Y-%m-%d") if instance.end_date else None,
    }
    cache.set(cache_key, updated_booking, timeout=10) 




