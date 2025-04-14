from icecream import ic
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .util import debug
from django.http import HttpResponse, HttpResponseNotAllowed
from . import models
from . import forms
from . import tables
from .models import SleepingSpace
from .forms import SleepingSpaceForm
from .models import Product
from .forms import ProductForm
import json
from urllib.parse import urlencode
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Resource



        
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


def manual_user_registration(request):
    if request.method == 'POST':
        form = forms.UserForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            request.session['message'] = "Client created successfully"
            request.session['message_type'] = "success"
            return redirect('manual_user_registration')
        else:
            request.session['message'] = "Form data is not valid."
            request.session['message_type'] = "error"
    else:
        form = forms.UserForm()

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    return render(request, 'manual_user_registration.html', {
        'message': message,
        'message_type': message_type,
        'form': form,
    })

def empty_resident_view(request):
    availabilities = models.Available.objects.all()
    data = []
    for availability in availabilities:
        data.append({
            'available_date': availability.available_date,
            'product': str(availability.product),
            'places_left': availability.places_left
        })
    
    context = {
        'availabilities': data,
    }
    
    return render(request, 'available_empty_recedency.html', context)


def user_shelter_stay_count_view(request):
    users = models.Client.objects.all()
    selected_user = None
    user_bookings = []

    if request.method == 'GET':
        user_id = request.GET.get('user_id', '')
        if user_id:
            selected_user = get_object_or_404(models.Client, id=user_id)
            user_bookings = models.Booking.objects.filter(user=selected_user).select_related('product', 'product__host')
            for booking in user_bookings:
                booking.days_slept = (datetime.today().date() - booking.start_date).days

    context = {
        'users': users,
        'selected_user': selected_user,
        'user_bookings': user_bookings,
    }

    return render(request, 'user_shelter_stay_count.html', context)

def invoice_create(request):
    message = None
    message_type = None

    if request.method == 'POST':
        form = forms.InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('host_create_invoice') 
        else:
            message = "Please correct the errors below."
            message_type = "error"
    else:
        form = forms.InvoiceForm()

    return render(request, 'create_invoice.html', {
        'form': form,
        'message': message,
        'message_type': message_type,
    })

@login_required(login_url='/login/')
def host_bookings_view(request, host_id):
    debug(request, "host_bookings")
    # Not sure if we have a host login get so I just added the admin login instead
    if not request.user.is_superuser:
            message = "You do not have permission to view this page."
            return render(request, 'host_bookings.html', {'bookings': [], 'host': None, 'message': message})
    host = get_object_or_404(models.Host, id=host_id)
    bookings = models.Booking.objects.filter(product__host=host)
    return render(request, 'host_bookings.html', {'bookings': bookings, 'host': host})

def daily_bookings_view(request):
    today = timezone.now().date()
    bookings = models.Booking.objects.filter(check_in_date=today)
    return render(request, 'daily_bookings.html', {'bookings': bookings})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})


# def product_update(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         form = ProductForm(request.POST, instance=product)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')
#     else:
#         form = ProductForm(instance=product)
#     return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    elif request.method == 'GET':
        form = ProductForm(instance=product)
        return render(request, 'product_form.html', {'form': form})
    elif request.method == 'PUT':
        form = ProductForm(request.POST) #, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponseNotAllowed(['POST', 'GET', 'PUT'])


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


def create_sleeping_space(request):
    if request.method == 'POST':
        form = SleepingSpaceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_sleeping_spaces')
    else:
        form = SleepingSpaceForm()
    return render(request, 'sleeping_space_form.html', {'form': form})


def update_sleeping_space(request, pk):
    sleeping_space = get_object_or_404(SleepingSpace, pk=pk)
    if request.method == 'POST':
        form = SleepingSpaceForm(request.POST, instance=sleeping_space)
        if form.is_valid():
            form.save()
            return redirect('list_sleeping_spaces')
    else:
        form = SleepingSpaceForm(instance=sleeping_space)
    return render(request, 'sleeping_space_form.html', {'form': form})


def list_sleeping_spaces(request):
    sleeping_spaces = SleepingSpace.objects.all()
    return render(request, 'sleeping_space_list.html', {'sleeping_spaces': sleeping_spaces})


def delete_sleeping_space(request, pk):
    sleeping_space = get_object_or_404(SleepingSpace, pk=pk)
    if request.method == 'POST':
        sleeping_space.delete()
        return redirect('list_sleeping_spaces')
    return render(request, 'sleeping_space_confirm_delete.html', {'sleeping_space': sleeping_space})




EU_COUNTRIES = [
    "Sweden", "Germany", "France", "Spain", "Italy", "Finland", "Denmark", "Poland",
    "Austria", "Netherlands", "Belgium", "Ireland", "Portugal", "Czech", "Greece",
    "Slovakia", "Slovenia", "Lithuania", "Latvia", "Estonia", "Hungary", "Croatia",
    "Luxembourg", "Bulgaria", "Romania", "Cyprus", "Malta","Browntown"
]
def resource_list(request):
    resources = Resource.objects.all()
    
    if request.GET.get('open_now'):
        # Filter resources that are currently open
        resources = [r for r in resources if r.is_open_now()]

    if request.GET.get('eu_citizen'):
        resources = [
            r for r in resources 
            if any(country.lower() in r.address.lower() for country in EU_COUNTRIES)
        ]

    age_filter = request.GET.getlist('target_group')
    if age_filter:
        resources = [r for r in resources if r.target_group in age_filter]

    return render(request, 'resource_list.html', {
        'resources': resources,
        'open_now': request.GET.get('open_now'),
        'eu_citizen': request.GET.get('eu_citizen'),
        'target_group_filter': age_filter,  # 👈 This line is important!
    })