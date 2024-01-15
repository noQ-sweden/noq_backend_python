from django.shortcuts import render, redirect
from django.http import HttpResponse

from . import models
from . import forms


def index_view(request):
    myhosts = {}
    if request.method == "POST":
        form = forms.IndexForm(request.POST)
        if form.is_valid():
            # form.save()
            myhosts = models.Host.objects.all()
    else:
        form = forms.IndexForm()
    return render(request, "index.html", {"form": form, "hosts": myhosts})


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


def book_room_view(request, host_id):
    form = forms.BookRoomForm()
    myhosts = models.Host.objects.all()
    return render(request, "book_room.html", {"form": form})
    return host_id
    rooms = {}
    host = models.Host.objects.get(host_id)
    name = host.name
    if request.method == "POST":
        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
           render(request, "book_room.html", {"form": form})
    else:
        form = forms.BookRoomForm()
    return render(request, "book_room.html", {"form": form})


def user_view(request):
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
