'''
Questions:
- Can we get what we need by subclassing Model?
'''
from django.db import models
from django.db.models.fields import IntegerField
from django.db.models.query import QuerySet
from django.db.models import Manager
from django.db.models import Field, CharField, ForeignKey
import django.db.models.fields.related

import JeevesLib
from JeevesLib import fexpr_cast
from eval.Eval import partialEval
from fast.AST import Facet, FObject, Unassigned, get_var_by_name, FExpr

import string
import random
import itertools

class JeevesQuerySet(QuerySet):
  def get_jiter(self):
    self._fetch_all()

    def get_env(obj, fields, env):
      vs = unserialize_vars(obj.jeeves_vars)
      for var_name, value in vs.iteritems():
        if var_name in env and env[var_name] != value:
          return None
        env[var_name] = value
      for field, subs in fields.iteritems():
        if field and get_env(getattr(obj, field), subs, env) is None:
          return None
      return env

    results = []
    for obj in self._result_cache:
      env = get_env(obj, self.query.select_related, {})
      if env is not None:
        results.append((obj, env))
    return results

  def get(self, **kwargs):
    l = self.filter(**kwargs).get_jiter()
    if len(l) == 0:
      raise Exception("wow such error: get() returned no values")
    
    for (o, _) in l:
      if o.jeeves_id != l[0][0].jeeves_id:
        raise Exception("wow such error: get() found rows for more than one jeeves_id")

    cur = Unassigned("")
    for (o, conditions) in l:
      old = cur
      cur = FObject(o)
      for var_name, val in conditions.iteritems():
        if val:
          cur = Facet(get_var_by_name(var_name), cur, old)
        else:
          cur = Facet(get_var_by_name(var_name), old, cur)
    try:
      return partialEval(cur, JeevesLib.jeevesState.pathenv.conditions)
    except TypeError:
      raise Exception("wow such error: could not find a row for every condition")

  def filter(self, **kwargs):
    l = []
    for argname, _ in kwargs.iteritems():
      t = argname.split('__')
      if len(t) > 0:
        l.append("__".join(t[:-1]))
    if len(l) > 0:
       return super(JeevesQuerySet, self).filter(**kwargs).select_related(*l)
    else:
       return super(JeevesQuerySet, self).filter(**kwargs)
      
  def exclude(self, **kwargs):
    raise NotImplementedError

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

def clone(old):
  new_kwargs = dict([(fld.name, getattr(old, fld.name)) for fld in old._meta.fields]);
  return old.__class__(**new_kwargs)

def serialize_vars(e):
  return ';' + ''.join('%s=%d;' % (var_name, var_value)
                        for var_name, var_value in e.iteritems())

def unserialize_vars(s):
  t = s[1:].split(';')
  e = {}
  for u in t:
    if u != "":
      v = u.split('=')
      e[v[0]] = bool(int(v[1]))
  return e

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

  def do_delete(self, e):
    if len(e) == 0:
      delete_query = self.__class__._objects_ordinary.filter(jeeves_id=self.jeeves_id)
      delete_query.delete()
    else:
      filter_query = self.__class__._objects_ordinary.filter(jeeves_id=self.jeeves_id)
      objs = list(filter_query)
      for obj in objs:
        eobj = unserialize_vars(obj.jeeves_vars)
        if any(var_name in eobj and eobj[var_name] != var_value
               for var_name, var_value in e.iteritems()):
          continue
        if all(var_name in eobj and eobj[var_name] == var_value
               for var_name, var_value in e.iteritems()):
          super(JeevesModel, obj).delete()
          continue
        addon = ""
        for var_name, var_value in e.iteritems():
          if var_name not in eobj:
            new_obj = clone(obj)
            if addon != "":
              new_obj.id = None # so when we save a new row will be made
            new_obj.jeeves_vars += addon + '%s=%d;' % (var_name, not var_value)
            addon += '%s=%d;' % (var_name, var_value)
            super(JeevesModel, new_obj).save()

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

      self.do_delete(e)

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

      self.do_delete(e)

  class Meta:
    abstract = True

  _objects_ordinary = Manager()

  def __eq__(self, other):
    if isinstance(other, FExpr):
      return other == self
    return isinstance(other, self.__class__) and self.jeeves_id == other.jeeves_id

class JeevesRelatedObjectDescriptor(property):
  def __init__(self, field):
    self.field = field
    self.cache_name = field.get_cache_name()

  def get_cache(self, instance):
    cache_attr_name = self.cache_name
    if hasattr(instance, cache_attr_name):
      cache = getattr(instance, cache_attr_name)
      if not isinstance(cache, dict):
        jid = getattr(instance, self.field.get_attname())
        assert not isinstance(jid, FExpr)
        cache = {jid : cache}
        setattr(instance, cache_attr_name, cache)
    else:
      cache = {}
      setattr(instance, cache_attr_name, cache)
    return cache

  def __get__(self, instance, instance_type):
    if instance is None:
      return self

    cache = self.get_cache(instance)
    def getObj(jeeves_id):
      if jeeves_id not in cache:
        cache[jeeves_id] = self.field.to.objects.get(jeeves_id=jeeves_id)
      return cache[jeeves_id]
    if instance is None:
      return self
    return JeevesLib.facetMapper(fexpr_cast(getattr(instance, self.field.get_attname())), getObj)

  def __set__(self, instance, value):
    cache = self.get_cache(instance)
    def getID(obj):
      if obj is None:
        return None
      if obj.jeeves_id is None:
        raise Exception("Object must be saved before it can be attached via JeevesForeignKey.")
      cache[obj.jeeves_id] = obj
      return obj.jeeves_id
    ids = JeevesLib.facetMapper(fexpr_cast(value), getID)
    setattr(instance, self.field.get_attname(), ids)

from django.db.models.fields.related import ForeignObject
class JeevesForeignKey(ForeignObject):
  requires_unique_target = False
  def __init__(self, to, *args, **kwargs):
    self.to = to

    for f in self.to._meta.fields:
      if f.name == 'jeeves_id':
        self.join_field = f
        break
    else:
      raise Exception("Need jeeves_id field")

    super(JeevesForeignKey, self).__init__(to, [self], [self.join_field], *args, **kwargs)
    self.db_constraint = False

  def contribute_to_class(self, cls, name, virtual_only=False):
    super(JeevesForeignKey, self).contribute_to_class(cls, name, virtual_only=virtual_only)
    setattr(cls, self.name, JeevesRelatedObjectDescriptor(self))

  def get_attname(self):
    return '%s_id' % self.name
  
  def get_attname_column(self):
    attname = self.get_attname()
    column = self.db_column or attname
    return attname, column

  def db_type(self, connection):
    return IntegerField().db_type(connection=connection)

  def get_path_info(self):
    opts = self.to._meta
    from_opts = self.model._meta
    return [django.db.models.fields.related.PathInfo(from_opts, opts, (self.join_field,), self, False, True)]

  def get_joining_columns(self):
    return ((self.column, self.join_field.column),)

  @property
  def foreign_related_fields(self):
    return (self.join_field,)

  @property
  def local_related_fields(self):
    return (self,)

  @property
  def related_fields(self):
    return ((self, self.join_field),)

  @property
  def reverse_related_fields(self):
    return ((self.join_field, self),)

  def get_extra_restriction(self, where_class, alias, related_alias):
    return None

  def get_cache_name(self):
    return '_jfkey_cache_' + self.name
