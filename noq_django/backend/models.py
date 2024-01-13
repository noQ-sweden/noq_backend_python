from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime


class Host(models.Model):
    name = models.CharField(max_length=80)
    street = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    count_of_available_places = models.IntegerField()
    total_available_places = models.IntegerField()

    class Meta:
        db_table = "hosts"

    def __str__(self) -> str:
        rsrv_count = Reservation.objects.filter(host=self).count()
        
        return f"{self.name}, {self.city} ({rsrv_count})"


class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    unokod = models.CharField(max_length=20)
    
    class Meta:
        db_table = "users"
        
    def first_reservation(self):
        """Första bokningen för denne user"""
        first_booking = Reservation.objects.filter(user=self).order_by('start_date').first()
        return first_booking.booking_date if first_booking else None

    def __str__(self) -> str:
        rsrv = Reservation.objects.filter(user=self).order_by('-start_date').first()
        
        startdate = ""
        if rsrv:
            startdate = rsrv.start_date
            
        return f"{self.name} ({startdate})"


class Reservation(models.Model):
    start_date = models.DateField()
    # End date default to start_date +1 ?
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.start_date} {self.user.name} [{self.host.name} {self.host.city}]"
    
    class Meta:
        db_table = "reservations"
        
    
    def save(self, *args, **kwargs):

        nbr_available = self.host.total_available_places
        
        booked = Reservation.objects.filter(host=self.host, start_date = self.start_date).count()
        
        if booked + 1 >nbr_available:
            raise ValidationError(("Host is fully booked"), code="full")

        # Check if there is another reservation for the same user and date
        existing_reservation = Reservation.objects.filter(user=self.user, start_date=self.start_date).first()
        
        if existing_reservation:
            raise ValidationError(("User already has a reservation for the same date."), code="already_booked")

        super().save(*args, **kwargs)



class Room(models.Model):
    description = models.CharField(max_length=100)
    total_places = models.IntegerField()
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=False)
    # active for future use to track if room is possible to book
    # effective_date for future use to track active status
   
    class Meta:
        db_table = "rooms"