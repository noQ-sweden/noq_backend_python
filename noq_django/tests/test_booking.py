from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.models import Booking, Product, BookingStatus, Available, Region, Client, User, Host, State
from datetime import datetime, timedelta

class TestBooking(TestCase):

    def setUp(self):
        self.region = Region.objects.create(name="City")
        self.host = Host.objects.create(name="Host", city="City", region=self.region)
        self.create_clients()
        self.create_products()
        self.create_booking_statuses()

    def create_clients(self):
        for i in range(4):
            user = User.objects.create(username=f"mr_{i}")
            Client.objects.create(
                first_name="John",
                last_name="Doe",
                gender="M",
                street="123 Main St",
                postcode="12345",
                city="New York",
                country="USA",
                phone="123-456-7890",
                email="john.doe@example.com",
                unokod="ABC123",
                day_of_birth=datetime.now().date(),
                personnr_lastnr="1234",
                region=self.region,
                requirements=None,
                last_edit=datetime.now().date(),
                user=user,
            )

        user = User.objects.create(username="Mrs_1")
        Client.objects.create(
            first_name="Mary",
            last_name="Doe",
            gender="K",
            street="123 Main St",
            postcode="12345",
            city="New York",
            country="USA",
            phone="123-456-7890",
            email="john.doe@example.com",
            unokod="ABC123",
            day_of_birth=datetime.now().date(),
            personnr_lastnr="1234",
            region=self.region,
            requirements=None,
            last_edit=datetime.now().date(),
            user=user,
        )

    def create_products(self):
        self.product_woman_only = Product.objects.create(
            name="Product",
            description="Description",
            total_places=10,
            host=self.host,
            type="woman-only",
            requirements=None,
        )
        self.product_one_place = Product.objects.create(
            name="ProductA",
            description="DescriptionA",
            total_places=1,
            host=self.host,
            type="room",
            requirements=None,
        )
        self.product_five_places = Product.objects.create(
            name="ProductB",
            description="DescriptionB",
            total_places=5,
            host=self.host,
            type="room",
            requirements=None,
        )

    def create_booking_statuses(self):
        BookingStatus.objects.bulk_create([
            BookingStatus(id=State.PENDING, description="pending"),
            BookingStatus(id=State.DECLINED, description="declined"),
            BookingStatus(id=State.ACCEPTED, description="accepted"),
            BookingStatus(id=State.CHECKED_IN, description="checked_in"),
            BookingStatus(id=State.IN_QUEUE, description="in_queue"),
            BookingStatus(id=State.RESERVED, description="reserved"),
            BookingStatus(id=State.CONFIRMED, description="confirmed"),
        ])

    def test_booking_with_valid_data(self):
        """Booking a product with valid data saves the booking and updates availability"""
        booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=3)).date(),
            product=Product.objects.first(),
            user=Client.objects.get(gender="K"),
            status=BookingStatus.objects.get(id=State.PENDING)
        )

        self.assertTrue(Booking.objects.filter(id=booking.id).exists())

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, booking.product.total_places - 1)

    def test_booking_with_invalid_date(self):
        """Booking a product with an invalid date raises ValidationError"""
        product = Product.objects.get(id=1)
        client = Client.objects.get(gender="K")
        status = BookingStatus.objects.first()

        booking = Booking(
            start_date=(datetime.now() - timedelta(days=1)).date(),
            end_date=(datetime.now() + timedelta(days=1)).date(),
            product=product,
            user=client,
            status=status
        )

        with self.assertRaises(ValidationError):
            booking.save()

        booking.start_date = datetime.now().date()
        booking.end_date = (datetime.now() - timedelta(days=1)).date()

        with self.assertRaises(ValidationError):
            booking.save()

    def test_booking_with_male_user_and_woman_only_type_raises_validation_error(self):
        """Booking a woman-only product with a male user raises ValidationError"""
        client = Client.objects.filter(gender="M").first()

        with self.assertRaises(ValidationError):
            Booking.objects.create(
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=1)).date(),
                product=self.product_woman_only,
                user=client,
                status=BookingStatus.objects.create(description="pending"),
            )

    def test_booking_with_same_user_and_date(self):
        """Booking a product with the same user and date as the current booking raises ValidationError"""
        booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=1)).date(),
            product=self.product_five_places,
            user=Client.objects.get(gender="K"),
            status=BookingStatus.objects.get(id=State.PENDING)
        )

        duplicate_booking = Booking(
            start_date=booking.start_date,
            end_date=(datetime.now() + timedelta(days=1)).date(),
            product=booking.product,
            user=Client.objects.get(gender="K"),
            status=booking.status
        )

        with self.assertRaises(ValidationError):
            duplicate_booking.save()

        self.assertTrue(Booking.objects.filter(id=booking.id).exists())

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, booking.product.total_places - 1)

    def test_booking_out_of_places(self):
        """Accepting a booking when out of places should raise error"""
        booking = Booking.objects.create(
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=2)).date(),
            product=self.product_one_place,
            user=Client.objects.get(id=1),
            status=BookingStatus.objects.get(id=State.PENDING)
        )

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, 0)

        booking_2 = Booking(
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=2)).date(),
            product=self.product_one_place,
            user=Client.objects.get(id=2),
            status=BookingStatus.objects.get(id=State.PENDING)
        )

        with self.assertRaises(ValidationError):
            booking_2.save()

        booking_2.status = BookingStatus.objects.get(id=State.IN_QUEUE)
        booking_2.save()

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, 0)

        booking.status = BookingStatus.objects.get(id=State.DECLINED)
        booking.save()

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, 1)

        booking_2.status = BookingStatus.objects.get(id=State.ACCEPTED)
        booking_2.save()

        availability = Available.objects.filter(
            product=booking.product,
            available_date=booking.start_date
        ).first()

        self.assertIsNotNone(availability)
        self.assertEqual(availability.places_left, 0)

    def create_five_bookings(self, test_date, product):
        """Make 5 bookings in different timespans."""
        test_data = [
            {'id': 1, 'start': 1, 'end': 4},
            {'id': 2, 'start': 0, 'end': 6},
            {'id': 3, 'start': 3, 'end': 8},
            {'id': 4, 'start': 0, 'end': 7},
            {'id': 5, 'start': 2, 'end': 5},
        ]
        clients = []
        for data in test_data:
            client = Client.objects.get(id=data['id'])
            clients.append(client)
            Booking.objects.create(
                start_date=test_date + timedelta(days=data['start']),
                end_date=test_date + timedelta(days=data['end']),
                product=product,
                user=client,
                status=BookingStatus.objects.get(id=State.PENDING)
            )
        return clients

    def test_that_availability_is_correct(self):
        """Make 5 bookings in different timespans. Test that the availability is counted correctly for different days."""
        expected_result = [3, 2, 1, 0, 1, 2, 3, 4, 5]
        booked_product = self.product_five_places
        test_date = datetime.now().date()
        self.create_five_bookings(test_date, booked_product)

        for i in range(8):
            availability = Available.objects.filter(
                product=booked_product,
                available_date=test_date + timedelta(days=i)
            ).first()
            self.assertIsNotNone(availability)
            self.assertEqual(availability.places_left, expected_result[i])

    def test_that_availability_is_correct_after_deletion(self):
        """Make 5 bookings in different timespans. Test that the availability is counted correctly when bookings are deleted."""
        expected_result = [
            [3, 3, 2, 1, 1, 2, 3, 4, 5],  # Step 1
            [4, 4, 3, 2, 2, 3, 3, 4, 5],  # Step 2
            [5, 5, 5, 5, 5, 5, 5, 5, 5]   # Step 3
        ]
        booked_product = self.product_five_places
        test_date = datetime.now().date()
        clients = self.create_five_bookings(test_date, booked_product)

        for i in range(3):
            if i > 1:
                Booking.objects.all().delete()
            else:
                client = clients[i]
                Booking.objects.filter(user=client).delete()

            for day_nr in range(8):
                availability = Available.objects.filter(
                    product=booked_product,
                    available_date=test_date + timedelta(days=day_nr)
                ).first()
                self.assertIsNotNone(availability)
                self.assertEqual(availability.places_left, expected_result[i][day_nr])