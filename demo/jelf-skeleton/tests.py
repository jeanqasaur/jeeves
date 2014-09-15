"""Sample tests.

    :synopsis: Sample tests. Run using "manage.py test."

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import datetime
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jelf.models import UserProfile

from jeevesdb import JeevesModel
import nose.tools as nt


class TestJelf(TestCase):
    def setUp(self):
        JeevesLib.init()

        self.alice = UserProfile.objects.create(
            username="alice", email="alice@mail.org")
        self.bob = UserProfile.objects.create(
                    username="bob", email="bob@mail.org")

    def test_email_view(self):
        self.assertEqual(JeevesLib.concretize(self.alice, self.alice.email)
            , "alice@mail.org")
        self.assertEqual(JeevesLib.concretize(self.bob, self.alice.email)
            , "[redacted]")

        self.assertEqual(
            JeevesLib.concretize(self.alice
                , UserProfile.objects.get(email="alice@mail.org"))
            , self.alice)
        self.assertEqual(
            JeevesLib.concretize(self.bob
                , UserProfile.objects.get(email="alice@mail.org"))
            , None)
