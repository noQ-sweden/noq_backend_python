from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime
from enum import IntEnum

class State(IntEnum):
    PENDING = 1
    DECLINED = 2
    ACCEPTED = 3
    CHECKED_IN = 4
    IN_QUEUE = 5
    RESERVED = 6
    CONFIRMED = 7

class Region(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        db_table = "regions"

    def __str__(self) -> str:
        return self.name


class Requirement(models.Model):
    description = models.CharField(max_length=32)


class ClientRequirement(models.Model):
    requirements = models.ManyToManyField(Requirement)


class ProductRequirement(models.Model):
    requirements = models.ManyToManyField(Requirement)


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    gender = models.CharField(
        max_length=1, default=None, blank=True
    )  # [('N','-'),('M', 'Man'), ('F', 'Kvinna')]
    street = models.CharField(max_length=80, default="")
    postcode = models.CharField(max_length=5, default="")

    city = models.CharField(max_length=80, default="")
    country = models.CharField(max_length=25, default="")

    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=40)

    unokod = models.CharField(max_length=10)
    day_of_birth = models.DateField(default=None, null=True)
    personnr_lastnr = models.CharField(max_length=4, default="")

    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=False, blank=False
    )

    requirements = models.ForeignKey(
        ClientRequirement, on_delete=models.CASCADE, null=True, blank=True
    )

    # Datum för senaste uppdateringen av användarodellen, för att avgöra om användaren är aktiv
    last_edit = models.DateField(verbose_name="Senaste Aktivitet")

    class Meta:
        db_table = "client"

        verbose_name_plural = "client"

    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if (
            "fake_data" in kwargs
        ):  # Om data är genererat av script använd istället för time.now
            self.last_edit = kwargs.pop("fake_data")
            super(Client, self).save(*args, **kwargs)
        else:
            self.last_edit = datetime.today()
            super(Client, self).save(*args, **kwargs)

    def __str__(self) -> str:
        # rsrv = ProductBooking.objects.filter(user=self).order_by("-start_date").first()

        # startdate = ""
        # if rsrv:
        #     startdate = rsrv.start_date

        return f"{self.first_name} {self.last_name}"


class Host(models.Model):
    users = models.ManyToManyField(User)
    name = models.CharField(max_length=80)
    street = models.CharField(max_length=80)
    postcode = models.CharField(max_length=5, default="")
    city = models.CharField(max_length=80, default="")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=False, blank=False
    )
    blocked_clients = models.ManyToManyField(Client)

    class Meta:
        db_table = "hosts"

    def __str__(self) -> str:
        return f"{self.name}, {self.city}"


class Product(models.Model):
    """
    Product är en generalisering som möjliggör att ett härbärge
    kan ha flera olika rumstyper och även annat som Lunch i gemenskap
    """
    TYPE_CHOICES = [
        ('room', 'Room'),
        ('woman-only', 'Woman Only'),
    ]

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    total_places = models.IntegerField()
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=12, choices=TYPE_CHOICES)
    requirements = models.ForeignKey(
        ProductRequirement, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        db_table = "product"

    def __str__(self) -> str:
        # available = None  # ProductAvailable.objects.filter(product=self).first()

        # if available:
        #     left = available.places_left
        #     return f"{self.description} på {self.host.name}, {self.host.city} {left} platser kvar"

        return f"{self.description} på {self.host.name}, {self.host.city}"
        # booking_count = ProductBooking.objects.filter(product=self).count()

        # return f"{self.description} ({self.total_places} platser på {self.host.name}, {self.host.city} ({booking_count} bokade)"

class BookingStatus(models.Model):
    description = models.CharField(max_length=32)

class Booking(models.Model):
    """
    Booking är en bokning av en produkt av en User
    Se också regelverk vid Save()
    """
    booking_time = models.DateTimeField(auto_now_add=True, verbose_name="Bokningsdatum")
    start_date = models.DateField(verbose_name="Datum")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, verbose_name="Plats"
    )
    user = models.ForeignKey(
        Client, on_delete=models.CASCADE, blank=False, verbose_name="Namn"
    )
    status = models.ForeignKey(
        BookingStatus, on_delete=models.CASCADE, blank=False, verbose_name="Beskrivning"
    )

    class Meta:
        db_table = "product_booking"

    # return count of accepted, pending and checked_in bookings
    def save(self, *args, **kwargs):

        # Check that the booked date is not in the past
        if str(self.start_date) < str(datetime.today().date()):
            raise ValidationError(
                ("Fel: Bokningen börjar före dagens datum!"),
                code="Date error",
            )
        # Check gender for room type = "woman-only"
        product_type = self.product.type

        if product_type == "woman-only":
            if self.user.gender != "K":
                # print("woman-only", self.user.gender, "nekad")
                raise ValidationError(
                    f"Rum för kvinnor kan inte bokas av män",
                    code="woman-only",
                )

        # Check if there is another booking for the same user and date
        existing_booking = Booking.objects.filter(
            user=self.user, start_date=self.start_date
        ).first()

        if existing_booking and self.id != existing_booking.id:
            raise ValidationError(
                ("Har redan en bokning samma dag!"),
                code="already_booked",
            )

        # Check for special rules
        # if product_type == "woman-only":
        #     print("\nRum för kvinnor OK:", self.user.name())

        # Check if there is free places available for booking
        # booking count is only valid if booking has status pending
        # in_queue or declined will not book a place
        # accepted, reserved, confirmed or checked_in already have
        # a booked place
        if self.status.id == State.PENDING:
            bookings_count = self.bookings_count()
            if bookings_count >= self.product.total_places:
                raise ValidationError(("Fullbokat rum"), code="full")

        super().save(*args, **kwargs)

        # Uppdatera Available
        self.calc_available()

    def bookings_count(self):
        # Exclude bookings with status declined and in_queue
        count = Booking.objects.filter(
            Q(product=self.product)
            & Q(start_date=self.start_date)
            & ~Q(status=State.DECLINED)
            & ~Q(status=State.IN_QUEUE)
        ).count()

        return count

    def calc_available(self):
        places_left = self.product.total_places - self.bookings_count()

        existing_availability = Available.objects.filter(
            product=self.product, available_date=self.start_date
        ).first()

        if existing_availability:
            existing_availability.places_left = places_left
            existing_availability.save()
        else:
            product_available = Available(
                available_date=self.start_date,
                product=Product.objects.get(id=self.product.id),
                places_left=places_left,
            )
            product_available.save()

    # Your custom code to be executed before the object is deleted
    def pre_delete_booking(self, instance, **kwargs):
        self.calc_available()
        print(f"Booking {instance} is about to be deleted.")

    def __str__(self) -> str:
        return f"{self.start_date}: {self.user.first_name} {self.user.last_name} har bokat {self.product.description} på {self.product.host.name}, {self.product.host.city}"

class BookingUpdate(models.Model):
    # This is a log to keep track of all changes done to bookings
    # Refences to other models are not used so we have audit log even if
    # user or status is deleted or changed later on.
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, verbose_name="Plats"
    )
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="Ändringstid")
    old_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32)
    username = models.CharField(max_length=32)

class Available(models.Model):
    available_date = models.DateField(verbose_name="Datum")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, verbose_name="Bokning"
    )
    places_left = models.IntegerField(verbose_name="Platser kvar", default=0)

    class Meta:
        db_table = "product_available"

    def __str__(self) -> str:
        return f"{self.product.description} på {self.product.host.name}, {self.product.host.city} har {self.places_left} platser kvar"
