from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from testdb.models import Animal

class TestJeevesModel(TestCase):
  def setUp(self):
    JeevesLib.init()

    Animal.objects.create(name='lion', sound='roar')
    Animal.objects.create(name='cat', sound='meow')
    Animal.objects.create(name='fox', sound='what')

  def testWrite(self):
    lion = Animal._objects_ordinary.get(name='lion')
    self.assertEquals(lion.name, 'lion')
    self.assertEquals(lion.sound, 'roar')
    self.assertEquals(lion.jeeves_vars, ';')

  #def test_animals_can_sound(self):
  #  lion = Animal.objects.get(name="lion")
  #  cat = Animal.objects.get(name="cat")
  #  fox = Animal.objects.get(name="fox")
  #  self.assertEqual(lion.speak(), 'The lion says "roar"')
  #  self.assertEqual(cat.speak(), 'The cat says "meow"')
  #  self.assertEqual(cat.speak(), 'The fox says "what"')
