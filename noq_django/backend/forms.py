# yourapp/forms.py

from django import forms
from django.urls import reverse, reverse_lazy

from datetime import datetime, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Field, MultiField, Div, Layout

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
        fields = ["host", "user"]


class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "phone"]


class AvailableProducts(forms.ModelForm):
    class Meta:
        model = models.ProductBooking
        fields = ("start_date", "product", "user")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout("product", "user")
        