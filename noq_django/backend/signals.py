from django.dispatch import receiver
from django.db.models.signals import post_delete
from backend.models import Booking


@receiver(post_delete, sender=Booking)
def delete_booking_signal(sender, instance, **kwargs):
    # Update available places when booking is deleted.
    instance.calc_available()




