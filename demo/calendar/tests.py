"""Calendar tests.

    :synopsis: Tests for the calendar study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import datetime
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from calendar.models import UserProfile, Event, EventHost, EventGuest

from jeevesdb import JeevesModel
import nose.tools as nt


class TestJelf(TestCase):
    def setUp(self):
        JeevesLib.init()

        self.aliceUser = UserProfile.objects.create(
            username="alice"
            , email="alice@mail.org")
        self.bobUser = UserProfile.objects.create(
            username="bob"
            , email="bob@mail.org")
        self.eveUser = UserProfile.objects.create(
            username="eve"
            , email="eve@mail.org")

    def test_get_sample_data(self):
        eve = UserProfile.objects.get(username="eve")
        self.assertEqual(JeevesLib.concretize(eve, eve), self.eveUser)
