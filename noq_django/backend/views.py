from django.shortcuts import render, redirect
from django.http import HttpResponse

from . import models
from . import forms


def index(request):
    return HttpResponse("Welcome to NoQ")


def reservation_view(request):
    if request.method == "POST":
        form = forms.ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "success_page"
            )  # Redirect to a success page or another appropriate URL
    else:
        form = forms.ReservationForm()
    myhosts = models.Host.objects.all()
    return render(request, "reservation.html", {"form": form, "hosts": myhosts})
