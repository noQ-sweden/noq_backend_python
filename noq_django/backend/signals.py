# from django.dispatch import receiver
# from django.db.models.signals import post_delete
# from backend.models import Booking
# from django.conf import settings
# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from rest_framework.authtoken.models import Token

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

# @receiver(post_delete, sender=Booking)
# def delete_booking_signal(sender, instance, **kwargs):
#     # Update available places when booking is deleted.
#     #instance.calc_available()




