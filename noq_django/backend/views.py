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
    queryset = models.Available.objects.filter(available_date=datum).all()

    # queryset = models.Product.objects.all()  # Customize the query as needed
    available = tables.AvailableProducts(queryset)
    # ic(available)
    # for a in queryset:
    #     ic(a)
    idag: datetime = datetime.strptime(datum, "%Y-%m-%d")
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


def book_room_view(request, available_id):
    message = ""
    available = models.Available.objects.filter(id=available_id).first()
    if not available:
        return redirect("")  # Main
    if request.method == "POST":
        # form = forms.BookRoomConfirmForm(request.POST)
        user_id = request.POST["userid"]
        if user_id:
            product = available.product
            user = models.UserDetails.objects.filter(pk=user_id).first()
            booking = models.Booking(
                    start_date=available.available_date,
                    product=product,
                    user=user,
                )

            booking.save()
            return redirect("index_view")  # Main

            
        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
            namn = form["brukare"].data
            user = models.UserDetails.objects.filter(first_name=namn).first()
            if user:
                form = forms.BookRoomConfirmForm(initial={"user": user})
                return render(
                    request,
                    "book_room_confirm.html",
                    {"form": form, "available": available, "user": user},
                )
            else:
                message = "Kan inte hitta någon med det förnamnet: " + namn  

    form = forms.BookRoomForm()
    return render(
        request,
        "book_room.html",
        {"form": form, "available": available, "message": message},
    )

    form = forms.BookRoomForm()
    myhosts = models.Host.objects.all()
    return render(request, "book_room.html", {"form": form})
    return available_id
    rooms = {}
    host = models.Host.objects.get(available_id)
    name = host.name
    if request.method == "POST":
        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
            render(request, "book_room.html", {"form": form})
    else:
        form = forms.BookRoomForm()
    return render(request, "book_room.html", {"form": form})
