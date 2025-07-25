from ninja import NinjaAPI, Schema, ModelSchema
from typing import Optional
from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    Available,
    Invoice,
    Activity,
    VolunteerActivity
)

from typing import List, Dict
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date, timedelta, datetime
from pydantic import BaseModel

date_string: str


class ClientSchema(ModelSchema):
    """

    Region

    Exempelvis Stockholm City och Farsta

    Varje Host tillhör en Region
    """

    class Meta:
        model = Client
        exclude =\
            ["user", "gender", "street", "postcode", "city", "country",
             "phone", "email", "day_of_birth", "personnr_lastnr",
             "region", "requirements", "last_edit", "flag"]


class SimplifiedClientSchema(Schema):
    id: int
    first_name: str
    last_name: str
    unokod: str
    region_name: Optional[str] = None


class RegionSchema(ModelSchema):
    """

    Region

    Exempelvis Stockholm City och Farsta

    Varje Host tillhör en Region
    """

    class Meta:
        model = Region
        fields = "__all__"



class UserSchema(ModelSchema):
    """
    User - för både Brukare och användare i systemet

    Varje user tillhör en Region
    """

    region: RegionSchema
    first_name: str # Add first name
    last_name: str # Add last name
    flag: bool # Add flag to user flase=ok, true=Danger

    class Meta:
        model = Client
        fields = "__all__"

class UserInfoSchema(Schema):
    """
    schema för att registrera en ny brukare
    """
    email: str
    password: Optional[str] = None
    first_name: str
    last_name: str
    phone: str
    gender: str
    street: str
    postcode: str
    city: str
    country: str
    region: int  # ID för region
    day_of_birth: Optional[date] = None
    personnr_lastnr: Optional[str] = None

class UserPostSchema(Schema):
    """
    User för POST-anrop

    """

    first_name: str
    last_name: str
    gender: str
    phone: str
    email: str
    region_id: int
    unokod: str = None

class UserRegistrationSchema(Schema):
    email: str
    password: str
    first_name: str
    last_name: str

class UserIDSchema(Schema):
    id: int


class HostSchema(ModelSchema):
    """

    Host

    Exempelvis Stadsmissionen, Stockholm

    Varje Host tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = Host
        exclude = ("blocked_clients","users","caseworkers",)


# Mall för Add dvs POST
class HostPostSchema(ModelSchema):
    """
    Host eller Härbärge för POST

    """

    class Meta:
        model = Host
        exclude = ["id", "region"]
        fields = "__all__"


class HostPatchSchema(Schema):
    """
    Host eller Härbärge för PATCH (update)

    Video to learn: https://www.youtube.com/watch?v=OGUqBay7BP0&t=919s

    """

    name: Optional[str] = None
    street: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    region: Optional[RegionSchema] = None

    class Meta:
        model = Host
        fields = ["id"]  # Note: all these fields are required on model level
        fields_optional = "__all__"


class ProductSchema(Schema):
    """
    Product
    Product är en generalisering istället för exempelvis Room
    som gör det möjligt att Härbärge kan erbjuda många tjänster.
    Exempelvis rum eller luncher
    """

    id: int
    name: str
    description: str
    total_places: int
    host: HostSchema = None
    type: str

class ProductSchemaWithPlacesLeft(ProductSchema):
    places_left: int

class AvailableDateSchema(Schema):
    available_date: date

class ProductSchemaWithDates(ProductSchema):
    places_left: int
    available_dates: List[AvailableDateSchema]

class StatusSchema(Schema):
    description: str

class BookingSchema(Schema):
    """
    Booking för att bokningar av en Product

    """
    id: int
    status: StatusSchema
    booking_time: datetime
    start_date: date
    end_date: date
    product: ProductSchema
    user: UserSchema


class BookingPostSchema(Schema):
    """
    Booking för att boka en Product

    """

    start_date: date
    end_date: date
    product_id: int
    user_id: Optional[int] = None


class VolunteerBookingPostSchema(Schema):
    """
    Booking för att boka en Product

    """

    user_id: int
    start_date: date
    end_date: date
    product_id: int
    uno: str


class VolunteerCreateClientPostSchema(Schema):
    """
    For creating a Client

    """

    first_name: str
    last_name: str
    uno: str
    gender: str
    region: str

class ActivitySchema(ModelSchema):
    is_signed_up: bool = False

    class Config:
        model = Activity
        model_fields = ["id", "title", "description", "start_time", "end_time", "is_approved"]

class VolunteerActivitySchema(ModelSchema):
    activity: int
    volunteer: int
    registered_at: datetime

    class Config:
        model = VolunteerActivity
        model_fields = ["activity", "volunteer", "registered_at"]

class VolunteerActivityCreateSchema(ModelSchema):
    activity: int

    class Config:
        model = VolunteerActivity
        model_fields = ["activity"]


class BookingUpdateSchema(Schema):
    booking_id: int


class AvailableSchema(Schema):
    """
    Available för att kunna se om en Product har tillgängliga platser

    """

    id: int
    available_date: date
    product: ProductSchema
    places_left: int

class AvailablePerDateSchema(Schema):
    """
    Available för att kunna se tillgängliga platser för product över
    antal dagar
    """
    available_dates: Dict[str, List[AvailableSchema]]

class AvailableProductsSchema(Schema):
    host: HostSchema
    products: List[ProductSchemaWithPlacesLeft]

class AvailableHostProductsSchema(Schema):
    host: HostSchema
    products: List[ProductSchemaWithDates]

class BookingCounterSchema(Schema):
    pending_count: int
    arrivals_count: int
    departures_count: int
    current_guests_count: int
    available_products: Dict[str, int]

class LoginPostSchema(Schema):
    email: str
    password: str

class LoginSchema(Schema):
    login_status: bool
    message: str
    groups: Optional[List[str]] = None
    host: Optional[HostSchema] = None
    first_name: Optional[str] = None # add first name
    last_name: Optional[str] = None # add last name

class InvoiceCreateSchema(Schema):
    """
    Schema for creating an Invoice.
    """
    host: int
    amount: float
    description: Optional[str] = None
    due_date: Optional[date] = None
    currency: str
    invoice_number: str
    vat_rate: float
    sale_date: Optional[date] = None
    seller_vat_number: Optional[str] = None
    buyer_vat_number: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    status: str = 'open'


class InvoiceResponseSchema(ModelSchema):
    host: HostSchema

    class Config:
        model = Invoice
        model_fields = ['id', 'host', 'amount', 'description', 'status', 'due_date', 'currency', 'invoice_number', 'vat', 'vat_rate', 'sale_date', 'seller_vat_number', 'buyer_vat_number', 'buyer_name', 'buyer_address']



class UserStaySummarySchema(Schema):
    """
    Sammanfattning av användarens övernattningar, inklusive användarens ID,
    totalantal nätter och tillhörande värd.
    """
    total_nights: int
    start_date: date
    end_date: date
    host: HostSchema


class UserShelterStayCountSchema(Schema):
    user_id: int
    first_name: str
    last_name: str
    user_stay_counts: List[UserStaySummarySchema]


class ForgotPasswordSchema(Schema):
    """
    Schema för att begära en återställning av lösenordet.
    """
    username: str

class ResetPasswordSchema(Schema):
    token: str
    uidb64: str
    new_password: str

#---- API SCHEMAS ACTIVITIESUPDATESCHEMA ----#
class ActivityUpdateSchema(Schema):
    title: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_approved: Optional[bool]
    status: Optional[str]

class ResourceSchema(Schema):
    id: int
    name: str
    type: str
    opening_time: str   
    closing_time: str   
    address: str
    phone: str
    email: str
    target_group: str
    other: str
    applies_to: List[str]
    is_open_now: bool


class ResourcePostSchema(Schema):
    """
    Schema for creating new resources
    """
    name: str
    type: str
    opening_time: str
    closing_time: str
    address: str
    phone: str
    email: str
    target_group: str
    other: str
    applies_to: List[str]

class ResourcePatchSchema(Schema):
    """
    Schema for updating resources
    """
    name: Optional[str] = None
    type: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    target_group: Optional[str] = None
    other: Optional[str] = None
    applies_to: Optional[List[str]] = None


class VolunteersSchema(Schema):
    first_name: str
    last_name: str
    email: str
    date_joined: datetime

class TaskStatusSchema(Schema):
    status: str


class ActivitySchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["id", "title", "description", "start_time", "end_time", "is_approved"]

class VolunteerProfileSchema(Schema):
    id: int
    first_name: str
    last_name: str
    email: str
    date_joined: date
    registered_at: date

class ActivityDetailSchema(ActivitySchema):
    volunteers: List[VolunteerProfileSchema]

class ActivityCreateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]

class ActivityUpdateSchema(ModelSchema):
    class Config:
        model = Activity
        model_fields = ["title", "description", "start_time", "end_time", "is_approved"]


class SimpleVolunteerSchema(Schema):
    id: int
    first_name: str
    last_name: str

class ActivityListSchema(Schema):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    is_approved: bool
    volunteers: List[SimpleVolunteerSchema]
