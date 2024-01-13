from django.db import models


class Host(models.Model):
    name = models.CharField(max_length=80)
    address1 = models.CharField(max_length=80)
    address2 = models.CharField(max_length=80)
    count_of_available_places = models.IntegerField()
    total_available_places = models.IntegerField()

    class Meta:
        db_table = "hosts"

    def __str__(self) -> str:
        return f"{self.name} {self.address1}, {self.address2}"


class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    unokod = models.CharField(max_length=20)
    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return f"{self.name} {self.unokod}"


class Reservation(models.Model):
    start_date = models.DateField()
    # End date default to start_date +1 ?
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.host} {self.user_id} {self.start_date}"
    
    class Meta:
        db_table = "reservations"



class Room(models.Model):
    description = models.CharField(max_length=100)
    total_places = models.IntegerField()
    host = models.ForeignKey(Host, on_delete=models.CASCADE, blank=False)
    # active for future use to track if room is possible to book
    # effective_date for future use to track active status
   
    class Meta:
        db_table = "rooms"