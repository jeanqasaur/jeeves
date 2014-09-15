"""Sample tests.

    :synopsis: Sample tests. Run using "manage.py test."

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import datetime
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
import nose.tools as nt


class TestJelf(TestCase):
    def setUp(self):
        JeevesLib.init()

    def test_sample(self):
        pass
