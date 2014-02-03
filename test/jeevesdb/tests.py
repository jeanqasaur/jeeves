from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from testdb.models import Animal

def parse_vars_row(vs):
  d = {}
  for entry in vs.split(';')[1:-1]:
    name, val = entry.split('=')
    d[name] = bool(int(val))
  return d

# expected is a list
# [({name:'lion',...}, {var_name:True,...})]
def areRowsEqual(rows, expected):
  rows = list(rows)
  if len(rows) != len(expected):
    print 'got len %d, expected %d' % (len(rows), len(expected))
    return False
  for attrs_dict, vars_dict in expected:
    for r in rows:
      vars_dict1 = parse_vars_row(r.jeeves_vars)
      if (vars_dict == vars_dict1 and
          all(getattr(r, name) == val for name, val in attrs_dict.iteritems())):
          break
    else:
      print 'could not find', attrs_dict, vars_dict
      return False
  return True

class TestJeevesModel(TestCase):
  def setUp(self):
    JeevesLib.init()

    Animal.objects.create(name='lion', sound='roar')
    Animal.objects.create(name='cat', sound='meow')

    self.x = JeevesLib.mkLabel()
    self.y = JeevesLib.mkLabel()

    Animal.objects.create(name='fox',
        sound=JeevesLib.mkSensitive(self.x, 'Hatee-hatee-hatee-ho!',
            'Joff-tchoff-tchoff-tchoffo-tchoffo-tchoff!'))

    Animal.objects.create(name='a',
        sound=JeevesLib.mkSensitive(self.x,
            JeevesLib.mkSensitive(self.y, 'b', 'c'),
            JeevesLib.mkSensitive(self.y, 'd', 'e')))

  def testWrite(self):
    lion = Animal._objects_ordinary.get(name='lion')
    self.assertEquals(lion.name, 'lion')
    self.assertEquals(lion.sound, 'roar')
    self.assertEquals(lion.jeeves_vars, ';')

    fox = Animal._objects_ordinary.filter(name='fox').filter(jeeves_vars=';%s=1;'%self.x.name).all()[0]
    self.assertEquals(fox.sound, 'Hatee-hatee-hatee-ho!')
    fox = Animal._objects_ordinary.filter(name='fox').filter(jeeves_vars=';%s=0;'%self.x.name).all()[0]
    self.assertEquals(fox.sound, 'Joff-tchoff-tchoff-tchoffo-tchoffo-tchoff!')

    a = list(Animal._objects_ordinary.filter(name='a').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'a', 'sound':'b'}, {self.x.name:True, self.y.name:True}),
      ({'name':'a', 'sound':'c'}, {self.x.name:True, self.y.name:False}),
      ({'name':'a', 'sound':'d'}, {self.x.name:False, self.y.name:True}),
      ({'name':'a', 'sound':'e'}, {self.x.name:False, self.y.name:False}),
     ]))

  def testQueryDelete(self):
    Animal.objects.create(name='delete_test1',
        sound=JeevesLib.mkSensitive(self.x,
            JeevesLib.mkSensitive(self.y, 'b', 'c'),
            JeevesLib.mkSensitive(self.y, 'd', 'e')))
    Animal.objects.filter(name='delete_test1').filter(sound='b').delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test1').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test1', 'sound':'c'}, {self.x.name:True, self.y.name:False}),
      ({'name':'delete_test1', 'sound':'d'}, {self.x.name:False, self.y.name:True}),
      ({'name':'delete_test1', 'sound':'e'}, {self.x.name:False, self.y.name:False}),
     ]))

    an = Animal.objects.create(name='delete_test2',
        sound=JeevesLib.mkSensitive(self.x,
            JeevesLib.mkSensitive(self.y, 'b', 'c'),
            JeevesLib.mkSensitive(self.y, 'd', 'e')))
    with JeevesLib.PositiveVariable(self.x):
      an.delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test2').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test2', 'sound':'d'}, {self.x.name:False, self.y.name:True}),
      ({'name':'delete_test2', 'sound':'e'}, {self.x.name:False, self.y.name:False}),
     ]))

    an = Animal.objects.create(name='delete_test3', sound='b')
    with JeevesLib.PositiveVariable(self.x):
      an.delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test3').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test3', 'sound':'b'}, {self.x.name:False})
    ]))

    an = Animal.objects.create(name='delete_test4', sound='b')
    with JeevesLib.PositiveVariable(self.x):
      with JeevesLib.NegativeVariable(self.y):
        an.delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test4').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test4', 'sound':'b'}, {self.x.name:False}),
      ({'name':'delete_test4', 'sound':'b'}, {self.x.name:True, self.y.name:True}),
    ]) or areRowsEqual(a, [
      ({'name':'delete_test4', 'sound':'b'}, {self.y.name:True}),
      ({'name':'delete_test4', 'sound':'b'}, {self.y.name:False, self.x.name:False}),
    ]))

    an = Animal.objects.create(name='delete_test5',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
    with JeevesLib.PositiveVariable(self.x):
      an.delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test5').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test5', 'sound':'c'}, {self.x.name:False})
    ]))

    an = Animal.objects.create(name='delete_test6',
            sound=JeevesLib.mkSensitive(self.x, 'b', 'c'))
    with JeevesLib.PositiveVariable(self.y):
      an.delete()
    a = list(Animal._objects_ordinary.filter(name='delete_test6').all())
    self.assertTrue(areRowsEqual(a, [
      ({'name':'delete_test6', 'sound':'b'}, {self.x.name:True,self.y.name:False}),
      ({'name':'delete_test6', 'sound':'c'}, {self.x.name:False,self.y.name:False}),
    ]))
