from django.shortcuts import render, redirect
from django.http import HttpResponse

from . import models
from . import forms

def index (request):
    return HttpResponse("Welcome to NoQ")


def reservation_view(request):
    if request.method == 'POST':
        form = forms.ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect to a success page or another appropriate URL
    else:
        form = forms.ReservationForm()

    return render(request, 'reservation.html', {'form': form, 'hosts': get_available_hosts()})

def get_available_hosts():
    # Implement logic to get available hosts for a given date
    # This can include querying the database to find hosts that don't have reservations for the specified date
    # Adjust this logic based on your requirements
    return models.Host.objects.all()  # Example: Return all hosts for simplicity