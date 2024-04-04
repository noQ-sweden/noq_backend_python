from icecream import ic
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404

from .util import debug

from django.http import HttpResponse

from . import models
from . import forms
from . import tables


        
def main_view(request):
    debug(request, "main_view", "main.html")
    header = "NoQ - startsida"
    message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc dolor lacus, faucibus at ultrices sit amet, aliquam vitae libero. Nullam nisl diam, tempor quis massa sit amet, gravida facilisis diam. Integer pretium diam eu diam pellentesque dictum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nam et velit at augue eleifend luctus eget ut magna. Duis nisi elit, dictum sed pretium sed, vulputate vitae est. Nunc euismod finibus purus sit amet commodo. Aenean sem nunc, posuere quis ante sed, facilisis vulputate nisl. Donec aliquet, nulla vitae laoreet elementum, urna nunc eleifend ipsum, non facilisis arcu metus in mauris. Donec vitae dignissim tortor. Interdum et malesuada fames ac ante ipsum primis in faucibus."
    return render(request, "main.html", {"message": message, "header": header})


def search_view(request):
    debug(request, "search_view", "search.html")
    myhosts = {}
    if request.method == "POST":
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            # form.save()
            myhosts = models.Host.objects.all()
            return render(request, "search.html", {"form": form, "hosts": myhosts})
    else:
        form = forms.AvailableForm()
        debug("SearchForm", "search.html")
        return render(request, "search.html", {"form": form, "message": "NoQ"})


def available_list(request):
    debug(request, "available_list")

    datum = request.POST["datum"]
    debug(request, datum)
    queryset = models.Available.objects.filter(available_date=datum).all()

    available = tables.AvailableProducts(queryset)

    idag: datetime = datetime.strptime(datum, "%Y-%m-%d")
    imorgon = idag + timedelta(days=1)
    form = forms.AvailableForm(initial={"datum": imorgon})
    debug("AvailableForm", "available_list.html")
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

def book_room_view(request, available_id):
    """
        Input: available_id visar vad som valts.
        
        Flödet gör att denna anropas flera ggr
        1. GET från "Välj alternativ" -> visa upp "Ange namn på brukare"
        2. POST med "namn" -> bekräftelse eller begär bekräftelse på borttag
        3. POST med bekräftelse -> end
    
    """
    debug(request, "book_room_view, id=", available_id)
    message = ""
    
    available = models.Available.objects.filter(id=available_id).first()
    
    if not available:
        return redirect("search_view") 
    
    """
        Steg 1: Visa möjliga val        
    """
    if request.method == "GET":
        form = forms.BookRoomForm()
        return render(
            request,
            "book_room.html",
            {"form": form, "available": available, "message": message},
        )

    """
        Kontrollera om det finns en tidigare bokning och ta bort den        
    """
    booking_id = request.POST["booking_id"]
    if booking_id:
        old = models.Booking.objects.filter(pk=booking_id).first()
        if old:
            old.delete()
        # message = f"Borttagen: {old.product.description} {old.product.host.name}, {old.product.host.city}"


    if request.method == "POST":
        user_id = request.POST["userid"]
        
        if not user_id:
            """
                Steg 2 -> visa bekräftelse
            """
            form = forms.BookRoomForm(request.POST)
            if form.is_valid():
                namn = form["brukare"].data
                user = models.Client.objects.filter(first_name=namn).first()
                if user:
                    form = forms.BookRoomConfirmForm(initial={"user": user})
                    booking = models.Booking.objects.filter(
                        start_date=available.available_date, user=user
                    ).first()
                    if booking:
                        available = ""
                    debug(
                        "book_room_view",
                        "book_room_confirm.html",
                        "booking=",
                        booking,
                        "avail=",
                        available,
                        "user=",
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
                return render(
                    request,
                    "book_room.html",
                    {"form": form, "available": available, "message": message},
                )
                
        """
        
            Steg 3: If User exists, everything is OK, then make booking and goto end

        """
        if user_id:
            product = available.product
            user = models.Client.objects.filter(pk=user_id).first()
            booking = models.Booking(
                start_date=available.available_date,
                product=product,
                user=user,
            )
            booking.save()
            confirmation = f"{booking.product.description} {booking.product.host.name}, {booking.product.host.city}"
            debug("book_room_view", "main.html", "user=", user, confirmation)
            return render(
                request,
                "main.html",
                {
                    "message": message,
                    "user": user,
                    "booking": confirmation,
                    "datum": available.available_date,
                },
            )
        

