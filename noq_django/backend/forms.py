# yourapp/forms.py

from django import forms

from . import models

class ReservationForm(forms.ModelForm):
    class Meta:
        model = models.Reservation
        fields = ['host', 'start_date', 'user']
