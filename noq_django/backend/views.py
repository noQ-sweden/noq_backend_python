import logging
from icecream import ic
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404


from django.http import HttpResponse

from . import models
from . import forms
from . import tables


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def dbg(*args):
    for a in args:
        logger.debug(a)


def example(request):
    context = {"form": forms.ExampleForm()}
    return render(request, "example.html", context)


def available_list(request):
    dbg("available_list")

    datum = request.POST["datum"]
    dbg(request, datum)
    queryset = models.Available.objects.filter(available_date=datum).all()

    # queryset = models.Product.objects.all()  # Customize the query as needed
    available = tables.AvailableProducts(queryset)
    # ic(available)
    # for a in queryset:
    #     ic(a)
    idag: datetime = datetime.strptime(datum, "%Y-%m-%d")
    imorgon = idag + timedelta(days=1)
    form = forms.IndexForm(initial={"datum": imorgon})
    dbg("IndexForm", "available_list.html")
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


def main_view(request):
    dbg("main_view", "main.html")
    header = "NoQ - startsida"
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc dolor lacus, faucibus at ultrices sit amet, aliquam vitae libero. Nullam nisl diam, tempor quis massa sit amet, gravida facilisis diam. Integer pretium diam eu diam pellentesque dictum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nam et velit at augue eleifend luctus eget ut magna. Duis nisi elit, dictum sed pretium sed, vulputate vitae est. Nunc euismod finibus purus sit amet commodo. Aenean sem nunc, posuere quis ante sed, facilisis vulputate nisl. Donec aliquet, nulla vitae laoreet elementum, urna nunc eleifend ipsum, non facilisis arcu metus in mauris. Donec vitae dignissim tortor. Interdum et malesuada fames ac ante ipsum primis in faucibus."
    return render(request, "main.html", {"message": message, "header": header})


def search_view(request):
    dbg("search_view", "search.html")
    myhosts = {}
    if request.method == "POST":
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            # form.save()
            myhosts = models.Host.objects.all()
            return render(request, "search.html", {"form": form, "hosts": myhosts})
    else:
        form = forms.IndexForm()
        dbg("IndexForm", "search.html")
        return render(request, "search.html", {"form": form, "message": "NoQ"})


def book_room_view(request, available_id):
    message = ""
    available = models.Available.objects.filter(id=available_id).first()
    
    if not available:
        return redirect("")  # Main

    if request.method == "GET":
        dbg("GET book_room_view", "book_room.html")
        form = forms.BookRoomForm()
        return render(
            request,
            "book_room.html",
            {"form": form, "available": available, "message": message},
        )

    if request.method == "POST":
        # form = forms.BookRoomConfirmForm(request.POST)
        dbg(request, request.POST)
        user_id = request.POST["userid"]
        booking_id = request.POST["booking_id"]
        if booking_id:
            old = models.Booking.objects.filter(pk=booking_id).first()
            if old:
                old.delete()
            # message = f"Borttagen: {old.product.description} {old.product.host.name}, {old.product.host.city}"
        if user_id:
            product = available.product
            user = models.UserDetails.objects.filter(pk=user_id).first()
            booking = models.Booking(
                start_date=available.available_date,
                product=product,
                user=user,
            )
            dbg("POST book_room_view", product, message, "main.html", user)
            booking.save()
            confirmation = f'{booking.product.description} {booking.product.host.name}, {booking.product.host.city}'
            return render(
                request,
                "main.html",
                {"message": message, "user": user, "booking": confirmation, "datum": available.available_date},
            )

        form = forms.BookRoomForm(request.POST)
        if form.is_valid():
            namn = form["brukare"].data
            user = models.UserDetails.objects.filter(first_name=namn).first()
            if user:
                form = forms.BookRoomConfirmForm(initial={"user": user})
                booking = models.Booking.objects.filter(
                    start_date=available.available_date, user=user
                ).first()
                if booking:
                    available = ""
                dbg(
                    "POST book_room_view",
                    booking,
                    available,
                    "book_room_confirm.html",
                    user,
                )
                return render(
                    request,
                    "book_room_confirm.html",
                    {
                        "form": form,
                        "available": available,
                        "user": user,
                        "current": booking,
                    },
                )
            else:
                message = "Kan inte hitta någon med det förnamnet: " + namn

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
