from icecream import ic
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404


from django.http import HttpResponse

from . import models
from . import forms
from . import tables


def example(request):
    context = {"form": forms.ExampleForm()}
    return render(request, "example.html", context)


def available_list(request):
    datum = request.POST["datum"]
    queryset = (
        models.Booking.objects.filter(start_date=datum).select_related("product").all()
    )

    # queryset = models.Product.objects.all()  # Customize the query as needed
    available = tables.AvailableProducts(queryset)
    # ic(available)
    date_format = "%Y-%m-%d"
    for a in queryset:
        ic(a)
    idag: datetime = datetime.strptime(datum, date_format)
    imorgon = idag + timedelta(days=1)
    form = forms.IndexForm(initial={"datum": imorgon})
    return render(
        request,
        "available_list.html",
        {
            "table": available,
            "objects": queryset,
            "form": form,
            "bokningsdag": idag.strftime("%Y-%m-%d"),
        },
    )


def index_view(request):
    myhosts = {}
    if request.method == "POST":
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            # form.save()
            myhosts = models.Host.objects.all()
            return render(request, "search.html", {"form": form, "hosts": myhosts})
    else:
        form = forms.IndexForm()
    return render(request, "search.html", {"form": form, "hosts": myhosts})


def reservation_view(request):
    if request.method == "POST":
        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "success_page"
            )  # Redirect to a success page or another appropriate URL
    else:
        form = forms.BookRoomForm()
    myhosts = models.Host.objects.all()
    return render(request, "book_room.html", {"form": form, "hosts": myhosts})


def book_room_view(request, host_id):
    product = get_object_or_404(models.Product, host_id=host_id)
    return render(request, "book_room.html", {"obj": product})

    form = forms.BookRoomForm()
    myhosts = models.Host.objects.all()
    return render(request, "book_room.html", {"form": form})
    return host_id
    rooms = {}
    host = models.Host.objects.get(host_id)
    name = host.host_name
    if request.method == "POST":
        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
            render(request, "book_room.html", {"form": form})
    else:
        form = forms.BookRoomForm()
    return render(request, "book_room.html", {"form": form})
