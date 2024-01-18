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
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=False)
    total_available_places = models.IntegerField()

    class Meta:
        db_table = "hosts"

    def __str__(self) -> str:
        rsrv_count = Reservation.objects.filter(host=self).count()

        return f"{self.host_name}, {self.city}: {self.total_available_places} platser ({rsrv_count} reserverade totalt)"


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

    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        db_table = "users"

    def first_reservation(self):
        """Första bokningen för denne user"""
        first_booking = (
            Reservation.objects.filter(user=self).order_by("start_date").first()
        )
        return first_booking.booking_date if first_booking else None

    def name(self) -> str:
        return f"{self.first_name}, {self.last_name}"

    def __str__(self) -> str:
        # rsrv = ProductBooking.objects.filter(user=self).order_by("-start_date").first()

        # startdate = ""
        # if rsrv:
        #     startdate = rsrv.start_date

        return f"{self.first_name} {self.last_name}"


class Reservation(models.Model):
    start_date = models.DateField()
    # End date default to start_date +1 ?
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.start_date} {self.user.first_name} {self.user.last_name} [{self.host.host_name} {self.host.city}]"

    class Meta:
        db_table = "reservations"

    def save(self, *args, **kwargs):
        nbr_available = self.host.total_available_places

        booked = Reservation.objects.filter(
            host=self.host, start_date=self.start_date
        ).count()

        if booked + 1 > nbr_available:
            raise ValidationError(("Host is fully booked"), code="full")

        # Check if there is another reservation for the same user and date
        existing_reservation = Reservation.objects.filter(
            user=self.user, start_date=self.start_date
        ).first()

        if existing_reservation:
            raise ValidationError(
                ("User already has a reservation for the same date."),
                code="already_booked",
            )

        super().save(*args, **kwargs)


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
        return f"{self.description} på {self.host.host_name}, {self.host.city}"
        # booking_count = ProductBooking.objects.filter(product=self).count()

        # return f"{self.description} ({self.total_places} platser på {self.host.host_name}, {self.host.city} ({booking_count} bokade)"


class ProductBooking(models.Model):
    start_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    class Meta:
        db_table = "product_booking"
        
    def save(self, *args, **kwargs):
        nbr_available = self.product.total_places

        booked = ProductBooking.objects.filter(
            product=self.product, start_date=self.start_date
        ).count()

        if booked + 1 > nbr_available:
            raise ValidationError(("Host is fully booked"), code="full")

        # Check if there is another reservation for the same user and date
        existing_reservation = ProductBooking.objects.filter(
            user=self.user, start_date=self.start_date
        ).first()

        if existing_reservation:
            raise ValidationError(
                ("User already is booked the same date."),
                code="already_booked",
            )

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.start_date} har {self.user.first_name} {self.user.last_name} bokat {self.product.description} på {self.product.host.host_name}, {self.product.host.city}"
