'''
Questions:
- Can we get what we need by subclassing Model?
'''
from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Manager
from django.db.models import Field, CharField

import JeevesLib
from JeevesLib import fexpr_cast
from eval.Eval import partialEval

import string
import random
import itertools

class JeevesQuerySet(QuerySet):
  # methods that return a queryset subclass of the ordinary QuerySet
  # need to be overridden

  def values(self, *fields):
    raise NotImplementedError

  def values_list(self, *fields, **kwargs):
    raise NotImplementedError

  def dates(self, field_name, kind, order='ASC'):
    raise NotImplementedError

  def datetimes(self, field_name, kind, order='ASC', tzinfo=None):
    raise NotImplementedError

  def none(self):
    raise NotImplementedError



class JeevesManager(Manager):
  def get_queryset(self):
    return (super(JeevesManager, self).get_queryset()
              ._clone(klass=JeevesQuerySet)
              .order_by('jeeves_id')
           )

alphanum = string.digits + string.letters
sysrand = random.SystemRandom()
JEEVES_ID_LEN = 32
def get_random_jeeves_id():
  return "".join(alphanum[sysrand.randint(0, len(alphanum)-1)]
                    for i in xrange(JEEVES_ID_LEN))

# From python docs
def powerset(iterable):
  "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
  s = list(iterable)
  return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))

def serialize_vars(e):
  return ';' + ''.join('%s=%d;' % (var_name, var_value)
                        for var_name, var_value in e.iteritems())

def fullEval(val, env):
  p = partialEval(val, env)
  return p.v

# Make a Jeeves Model that enhances the vanilla Django model with information
# about how labels work and that kind of thing. We'll also need to override
# some methods so that we can create records and make queries appropriately.

class JeevesModel(models.Model):
  objects = JeevesManager()
  jeeves_id = CharField(max_length=JEEVES_ID_LEN, null=False)
  jeeves_vars = CharField(max_length=1024, null=False)

  def save(self, *args, **kw):
    if not self.jeeves_id:
      self.jeeves_id = get_random_jeeves_id()

    if kw.get("update_field", None) is not None:
      raise NotImplementedError("Partial saves not supported.")

    field_names = set()
    for field in self._meta.concrete_fields:
      if not field.primary_key and not hasattr(field, 'through'):
        field_names.add(field.attname)

    all_vars = []
    d = {}
    env = JeevesLib.jeevesState.pathenv.getEnv()
    for field_name in field_names:
      value = getattr(self, field_name)
      f = partialEval(fexpr_cast(value), env)
      all_vars.extend(v.name for v in f.vars())
      d[field_name] = f

    for p in powerset(all_vars):
      true_vars = list(p)
      false_vars = list(set(all_vars).difference(p))
      e = dict(env)
      e.update({tv : True for tv in true_vars})
      e.update({fv : False for fv in false_vars})

      delete_query = self.__class__._objects_ordinary.filter(jeeves_id=self.jeeves_id)
      for var_name, var_value in e.iteritems():
        delete_query = delete_query.filter(jeeves_vars__contains =
              ';%s=%d;' % (var_name, var_value))
      delete_query.delete()

      klass = self.__class__
      obj_to_save = klass(**{
        field_name : fullEval(field_value, e)
        for field_name, field_value in d.iteritems()
      })
      obj_to_save.jeeves_vars = serialize_vars(e)
      super(JeevesModel, obj_to_save).save(*args, **kw)

  def delete(self, *args, **kw):
    if self.jeeves_id is None:
      return

    field_names = set()
    for field in self._meta.concrete_fields:
      if not field.primary_key and not hasattr(field, 'through'):
        field_names.add(field.attname)

    all_vars = []
    d = {}
    env = JeevesLib.jeevesState.pathenv.getEnv()
    for field_name in field_names:
      value = getattr(self, field_name)
      f = partialEval(fexpr_cast(value), env)
      all_vars.extend(v.name for v in f.vars())
      d[field_name] = f

    for p in powerset(all_vars):
      true_vars = list(p)
      false_vars = list(set(all_vars).difference(p))
      e = dict(env)
      e.update({tv : True for tv in true_vars})
      e.update({fv : False for fv in false_vars})

      delete_query = self.__class__._objects_ordinary.filter(jeeves_id=self.jeeves_id)
      for var_name, var_value in e.iteritems():
        delete_query = delete_query.filter(jeeves_vars__contains =
              ';%s=%d;' % (var_name, var_value))
      delete_query.delete()

  class Meta:
    abstract = True

  _objects_ordinary = Manager()
