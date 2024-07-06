from django.dispatch import receiver
from django.db.models.signals import post_delete
from backend.models import Booking, Available, State
from datetime import datetime, timedelta
from django.db.models import Q

def get_places_by_date(start_date, end_date, product):
    # Return count for bookings for each day of the booking
    # TODO: investigate why end_date is datetime.date
    e_date = datetime.combine(end_date, datetime.max.time())
    type_e = type(e_date)
    type_s = type(start_date)
    date_delta = (end_date - start_date).days
    booking_counts = {}

    for i in range(date_delta):
        date_time = start_date + timedelta(days=i)
        count = Booking.objects.filter(
            Q(product=product)
            & Q(start_date__lte=date_time)
            & Q(end_date__gt=date_time)
            & ~Q(status=State.DECLINED)
            & ~Q(status=State.IN_QUEUE)
        ).count()
        date = f"{date_time:%Y-%m-%d}"
        booking_counts[date] = count

    return booking_counts


@receiver(post_delete, sender=Booking)
def delete_booking_signal(sender, instance, **kwargs):
    product = instance.product
    bookings_per_day = get_places_by_date(
        instance.start_date,
        instance.end_date,
        product
    )
    for date in bookings_per_day:
        places_left = product.total_places - bookings_per_day[date]

        existing_availability = Available.objects.filter(
            product=product, available_date=date
        ).first()

        if existing_availability:
            existing_availability.places_left = places_left
            existing_availability.save()
        else:
            product_available = Available(
                available_date=date,
                product=product,
                places_left=places_left,
            )
            product_available.save()




