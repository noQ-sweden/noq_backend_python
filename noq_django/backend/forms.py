from django import forms
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Field, MultiField, Div, Layout

from . import models
from .models import SleepingSpace



class AvailableForm(forms.Form):
    idag = datetime.now() + timedelta(days=0)
    datum = forms.DateField(initial=idag)

    class Meta:
        fields = ["datum"]


class SearchForm(forms.Form):
    idag = datetime.now() + timedelta(days=1)

    class Meta:
        fields = ["datum"]


class BookRoomForm(forms.Form):
    brukare = forms.CharField()

    labels = {"brukare": "Förnamn"}

    widgets = {
        "brukare": forms.TextInput(attrs={"class": "form-control"}),
    }

    class Meta:
        fields = ["host", "user"]


class BookRoomConfirmForm(forms.Form):
    userid = forms.IntegerField

    class Meta:
        fields = ["userid"]


class BookRoomForm2(forms.Form):
    förnamn = forms.CharField(required=False)
    efternamn = forms.CharField(required=False)

    class Meta:
        fields = ["förnamn", "efternamn", "user"]

        labels = {
            "förnamn": "",
            "efternamn": "",
        }

        widgets = {
            "förnamn": forms.TextInput(attrs={"class": "form-control"}),
            "efternamn": forms.TextInput(attrs={"class": "form-control"}),
        }


class BookForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    user_id = forms.IntegerField()
    product_id = forms.IntegerField()

    class Meta:
        fields = ["host", "user"]


class UserForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = [
            "first_name", "last_name", "gender", "phone", "email",
            "city", "street", "postcode", "unokod", "region"
        ]
        widgets = {
            'gender': forms.Select(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')]),
        }
        
    region = forms.ModelChoiceField(queryset=models.Region.objects.all(), required=True, label="Region")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if models.Client.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class AvailableProducts(forms.ModelForm):
    class Meta:
        model = models.Booking
        fields = ("start_date", "end_date", "product", "user")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout("product", "user")


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'description', 'total_places', 'host', 'type', 'requirements']

    def clean_host(self):
        host = self.cleaned_data.get('host')
        if not models.Host.objects.filter(id=host.id).exists():
            raise ValidationError("Den angivna värden finns inte")
        return host

    def clean_type(self):
        product_type = self.cleaned_data.get('type')
        if product_type not in ['room', 'woman-only']:
            raise ValidationError("Typ kan endast vara 'room' eller 'woman-only'.")
        return product_type
    

class InvoiceForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = models.Invoice
        fields = ['host', 'amount', 'description', 'status', 'due_date', 'currency', 'invoice_number']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['status'].initial = models.InvoiceStatus.objects.get(name='open')
        except models.InvoiceStatus.DoesNotExist:
            self.fields['status'].initial = None

class SleepingSpaceForm(forms.ModelForm):
    class Meta:
        model = SleepingSpace
        fields = ['bed_type', 'status']