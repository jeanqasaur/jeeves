"""Calendar tests.

    :synopsis: Tests for the calendar study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import date, datetime
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
        self.carolUser = UserProfile.objects.create(
            username="carol"
            , email="carol@mail.org")
        self.eveUser = UserProfile.objects.create(
            username="eve"
            , email="eve@mail.org")

        self.eveParty = Event.objects.create(
            name="Eve's surprise party"
            , location="Chuck E. Cheese's"
            , time=datetime(2014, 10, 24, 20, 0)
            , description="Don't tell Eve!"
        )

        self.otherParty = Event.objects.create(
            name="Other party"
            , location="Other location"
            , time=datetime(2014, 10, 24, 20, 0)
            , description="Nothing of note."
        )

        EventHost.objects.create(event=self.eveParty, host=self.aliceUser)
        EventHost.objects.create(event=self.eveParty, host=self.bobUser)
        EventGuest.objects.create(event=self.eveParty, guest=self.carolUser)

    def test_get_sample_data(self):
        eve = UserProfile.objects.get(username="eve")
        self.assertEqual(JeevesLib.concretize(eve, eve), self.eveUser)

    def test_event_host(self):
        self.assertTrue(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_host(self.aliceUser)))
        self.assertTrue(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_host(self.bobUser)))
        self.assertFalse(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_host(self.carolUser)))
        self.assertFalse(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_host(self.eveUser)))

    def test_event_guest(self):
        self.assertTrue(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_guest(self.carolUser)))
        self.assertFalse(
            JeevesLib.concretize(self.aliceUser
                , self.eveParty.has_host(self.eveUser)))

        self.assertTrue(
            JeevesLib.concretize(self.aliceUser
                , self.aliceUser.has_event(self.eveParty)))
        self.assertTrue(
            JeevesLib.concretize(self.aliceUser
                , self.bobUser.has_event(self.eveParty)))
        self.assertFalse(
            JeevesLib.concretize(self.aliceUser
                , self.eveUser.has_event(self.eveParty)))

    def test_view_email(self):
        self.assertEqual(
            JeevesLib.concretize(self.aliceUser, self.aliceUser.email)
            , "alice@mail.org")
        self.assertEqual(
            JeevesLib.concretize(self.aliceUser, self.eveUser.email)
            , "[redacted]")
