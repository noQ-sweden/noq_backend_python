from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime


class Region(models.Model):
    region_name = models.CharField(max_length=80)

    class Meta:
        db_table = "regions"

    def __str__(self) -> str:
        return self.region_name


class Host(models.Model):
    host_name = models.CharField(max_length=80)
    street = models.CharField(max_length=80)
    postcode = models.CharField(max_length=5, default="")
    city = models.CharField(max_length=80, default="")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=False, blank=False
    )
    total_available_places = models.IntegerField()

    class Meta:
        db_table = "hosts"

    def __str__(self) -> str:
        return f"{self.host_name}, {self.city}: {self.total_available_places} platser"


class User(models.Model):
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

    class Meta:
        db_table = "users"

    def name(self) -> str:
        return f"{self.first_name}, {self.last_name}"

    def __str__(self) -> str:
        # rsrv = ProductBooking.objects.filter(user=self).order_by("-start_date").first()

        # startdate = ""
        # if rsrv:
        #     startdate = rsrv.start_date

        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    """
    Product är en generalisering som möjliggör att ett härbärge
    kan ha flera olika rumstyper och även annat som Lunch i gemenskap
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    total_places = models.IntegerField()
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=12, default="")  # ex "endast kvinnor"

    class Meta:
        db_table = "product"

    def __str__(self) -> str:
        available = None  # ProductAvailable.objects.filter(product=self).first()

        if available:
            left = available.places_left
            return f"{self.description} på {self.host.host_name}, {self.host.city} {left} platser kvar"

        return f"{self.description} på {self.host.host_name}, {self.host.city}"
        # booking_count = ProductBooking.objects.filter(product=self).count()

        # return f"{self.description} ({self.total_places} platser på {self.host.host_name}, {self.host.city} ({booking_count} bokade)"


class Booking(models.Model):
    start_date = models.DateField(verbose_name="Datum")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, verbose_name="Plats"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, verbose_name="Brukare"
    )

    class Meta:
        db_table = "product_booking"

    def save(self, *args, **kwargs):
        self.start_date = self.start_date
        nbr_available = self.product.total_places

        # Check gender for room type = "woman-only"
        product_type = self.product.type

        if product_type == "woman-only":
            if self.user.gender != "K":
                print("woman-only", self.user.gender, "nekad")
                raise ValidationError(
                    f"Rum för kvinnor kan inte bokas av män",
                    code="woman-only",
                )

        # Is Host fully booked?
        booked = Booking.objects.filter(
            product=self.product, start_date=self.start_date
        ).count()

        if booked + 1 > nbr_available:
            raise ValidationError(("Fullbokat rum"), code="full")

        # Check if there is another booking for the same user and date
        existing_booking = Booking.objects.filter(
            user=self.user, start_date=self.start_date
        ).first()

        if existing_booking:
            raise ValidationError(
                ("Har redan en bokning samma dag!"),
                code="already_booked",
            )

        if product_type == "woman-only":
            print("woman-only", self.user.gender, self.user.first_name)

        super().save(*args, **kwargs)

        # Uppdatera ProductAvailable
        bookings = Booking.objects.filter(
            product=self.product, start_date=self.start_date
        ).count()

        left = self.product.total_places - bookings

        if bookings == 0:
            raise ValidationError("Bookings IS ZERO")

        availability_record = Available.objects.filter(product=self.product).first()

        if availability_record:
            availability_record.places_left = left
            availability_record.save()
        else:
            product_available = Available(
                available_date=self.start_date,
                product=Product.objects.get(id=self.product.id),
                places_left=left,
            )
            product_available.save()

    def __str__(self) -> str:
        return f"{self.start_date}: {self.user.first_name} {self.user.last_name} har bokat {self.product.description} på {self.product.host.host_name}, {self.product.host.city}"


class Available(models.Model):
    available_date = models.DateField(verbose_name="Datum")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, verbose_name="Bokning"
    )
    places_left = models.IntegerField(verbose_name="Platser kvar", default=0)

    class Meta:
        db_table = "product_available"

    def __str__(self) -> str:
        return f"{self.available_date}: {self.product.description} på {self.product.host.host_name}, {self.product.host.city} har {self.places_left} platser kvar"
