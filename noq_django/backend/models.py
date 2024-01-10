from django.db import models

class Host(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    address1 = models.CharField(max_length=80)
    address2 = models.CharField(max_length=80)
    count_of_available_places = models.IntegerField()
    total_available_places = models.IntegerField()
    
    class Meta:
        db_table = "hosts"
        managed = True
    
    def __str__(self) -> str:
        return f"{self.name} {self.address1}, {self.address2}"