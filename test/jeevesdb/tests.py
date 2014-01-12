from django.db import models
from django.utils import unittest
from django.test import TestCase

from jeevesdb import JeevesAPI, JeevesModel
from testdb.models import Animal

class TestJeevesModel(TestCase):
  def setUp(self):
    Animal.objects.create(name='lion', sound='roar')
    Animal.objects.create(name='cat', sound='meow')

  def test_animals_can_sound(self):
    """Animals that can sound are correctly identified"""
    lion = Animal.objects.get(name="lion")
    cat = Animal.objects.get(name="cat")
    self.assertEqual(lion.speak(), 'The lion says "roar"')
    self.assertEqual(cat.speak(), 'The cat says "meow"')
