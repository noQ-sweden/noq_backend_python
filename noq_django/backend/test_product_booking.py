import unittest
from icecream import ic
from django.test import TestCase

from .models import UserDetails, UserType, Product, Region, Booking


def test_first():
    value_2 = 5 - 3
    assert value_2 == 2


class test_ProductBooking(TestCase):
    def setUp(self):
        pass
        # user = User.objects.filter(name=tom.name)
        # if user is None:
        #     tom = User(name="Tom Sawyer", phone="123", email="a@e.se", unokod="UNO1234")
        #     tom.save()
        #     user = tom

    def test_user(self):
        man = UserType(name="Man")
        man.save()
        woman = UserType(name="woman")
        woman.save()

        user = UserDetails(
            name="Tom Sawyer",
            user_type=man,
            phone="123",
            email="a@e.se",
            unokod="UNO1234",
        )
        user.save()

        self.assertIsNotNone(user)

        product = Product("women-only")


if __name__ == "__main__":
    test_ProductBooking()
