# yourapp/forms.py

from django import forms
from datetime import datetime, timedelta
from . import models


class IndexForm(forms.Form):
    idag = datetime.now() + timedelta(days=1)
    datum = forms.DateField(initial=idag)

    class Meta:
        fields = ["datum"]

class SearchForm(forms.Form):
    idag = datetime.now() + timedelta(days=1)
    

    class Meta:
        fields = ["datum"]

class BookRoomForm(forms.Form):
    namn = forms.CharField()
    class Meta:
        fields = ["host","user"]


class ReservationForm(forms.ModelForm):
    class Meta:
        model = models.Reservation
        fields = ["host", "start_date", "user"]


class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "phone"]
