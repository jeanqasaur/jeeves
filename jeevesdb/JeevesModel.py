"""Jeeves database interface.

    :synopsis: Monkey-patching Django's QuerySet with Jeeves functionality.

.. moduleauthor: Travis Hance <tjhance7@gmail.com>
"""
from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Manager
from django.db.models import CharField
from django.db.models.loading import get_model
import django.db.models.fields.related

import JeevesLib
from JeevesLib import fexpr_cast
from fast.AST import Facet, FObject, Unassigned, FExpr, FNull
#from conf.settings import TEST_OPTIMIZATIONS as optimize_flag
import JeevesModelUtils

class JeevesQuerySet(QuerySet):
    """The Jeeves version of Django's QuerySet.
    """
    @JeevesLib.supports_jeeves
    def get_jiter(self):
        """Creates an iterator for the QuerySet.
        This is a JList?
        """
        self._fetch_all()

        def get_env(obj, fields, env):
            """Gets the Jeeves variable environment associated with the fields.
            """
            if hasattr(obj, "jeeves_vars"):
                jeeves_vars = JeevesModelUtils.unserialize_vars(obj.jeeves_vars)
            else:
                jeeves_vars = {}
            for var_name, value in jeeves_vars.iteritems():
                if var_name in env and env[var_name] != value:
                    return None
                env[var_name] = value
                acquire_label_by_name(self.model._meta.app_label, var_name)
            for field, subs in fields.iteritems() if fields else []:
                if field and get_env(getattr(obj, field), subs, env) is None:
                    return None
            return env

        results = []
        for obj in self._result_cache:
            env = get_env(obj, self.query.select_related, {})
            if env is not None:
                results.append((obj, env))
        return results

    def get(self, use_base_env=False, **kwargs):
        """Fetches a JList of rows that match the conditions.
        """
        matches = self.filter(**kwargs).get_jiter()
        if len(matches) == 0:
            return None

        for (row, _) in matches:
            if row.jeeves_id != matches[0][0].jeeves_id:
                raise Exception("wow such error: \
                    get() found rows for more than one jeeves_id")

        viewer = JeevesLib.get_viewer()
        has_viewer = not isinstance(viewer, FNull)
        if has_viewer:
            JeevesLib.reset_solverstate(viewer)

        cur = None
        for (row, conditions) in matches:
            old = cur
            cur = FObject(row)
            for var_name, val in conditions.iteritems():
                label = acquire_label_by_name(self.model._meta.app_label
                    , var_name)
                viewer = JeevesLib.get_viewer()
                if has_viewer:
                    # If we know the viewer, then we concretize.
                    if JeevesLib.assignLabel(viewer, label):
                        if not val:
                            cur = old
                    else:
                        if val:
                            cur = old
                else:
                    if val:
                        cur = Facet(label, cur, old)
                    else:
                        cur = Facet(label, old, cur)
        try:
            return cur.partialEval({} if use_base_env \
                else JeevesLib.jeevesState.pathenv.getEnv())
        except TypeError:
            raise Exception("wow such error: \
                could not find a row for every condition")

    def filter(self, **kwargs):
        """Jelf implementation of filter.
        """
        related_names = []
        for argname, _ in kwargs.iteritems():
            related_name = argname.split('__')
            if len(related_name) > 1:
                related_names.append("__".join(related_name[:-1]))
        if len(related_names) > 0:
            return super(
                    JeevesQuerySet, self).filter(
                        **kwargs).select_related(*related_names)
        else:
            return super(JeevesQuerySet, self).filter(**kwargs)

    @JeevesLib.supports_jeeves
    def all(self):
        viewer = JeevesLib.get_viewer()
        if isinstance(viewer, FNull):
            # If we don't know who the viewer is, create facets.
            elements = JeevesLib.JList2([])
            env = JeevesLib.jeevesState.pathenv.getEnv()
            for val, cond in self.get_jiter():
                popcount = 0
                for vname, vval in cond.iteritems():
                    if vname not in env:
                        # If we don't 
                        vlabel = acquire_label_by_name(
                                    self.model._meta.app_label, vname)
                        JeevesLib.jeevesState.pathenv.push(vlabel, vval)
                        popcount += 1
                    elif env[vname] != vval:
                        break
                else:
                    elements.append(val)
                for _ in xrange(popcount):
                    JeevesLib.jeevesState.pathenv.pop()
            return elements
        else:
            # Otherwise concretize early.
            elements = []
            env = JeevesLib.jeevesState.pathenv.getEnv()

            JeevesLib.reset_solverstate(viewer)
            for val, cond in self.get_jiter():
                for vname, vval in cond.iteritems():
                    if vname not in env:
                        vlabel = acquire_label_by_name(
                                    self.model._meta.app_label, vname)
                        if JeevesLib.assignLabel(viewer, vlabel) == vval:
                            elements.append(val)
            return elements


    @JeevesLib.supports_jeeves
    def delete(self):
        # can obviously be optimized
        # TODO write tests for this
        for val, cond in self.get_jiter():
            popcount = 0
            for vname, vval in cond.iteritems():
                if vname not in JeevesLib.jeevesState.pathenv.getEnv():
                    vlabel = acquire_label_by_name(
                                self.model._meta.app_label, vname)
                    JeevesLib.jeevesState.pathenv.push(vlabel, vval)
                    popcount += 1
            val.delete()
            for _ in xrange(popcount):
                JeevesLib.jeevesState.pathenv.pop()

    @JeevesLib.supports_jeeves
    def exclude(self, **kwargs):
        raise NotImplementedError

    # TODO: methods that return a queryset subclass of the ordinary QuerySet
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
    """The Jeeves version of Django's Manager class, which [...]
    """
    @JeevesLib.supports_jeeves
    def get_queryset(self):
        return (super(JeevesManager, self).get_queryset()
            ._clone(klass=JeevesQuerySet)
              .order_by('jeeves_id')
           )

    def all(self):
        return super(JeevesManager, self).all().all()

    @JeevesLib.supports_jeeves
    def create(self, **kw):
        elt = self.model(**kw)
        elt.save()
        return elt

def clone(old):
    """Returns a copy of an object.
    """
    new_kwargs = dict([(fld.name, getattr(old, fld.name))
                    for fld in old._meta.fields
                        if not isinstance(fld, JeevesForeignKey)])
    ans = old.__class__(**new_kwargs)
    for fld in old._meta.fields:
        if isinstance(fld, JeevesForeignKey):
            setattr(ans, fld.attname, getattr(old, fld.attname))
    return ans

def acquire_label_by_name(app_label, label_name):
    """Gets a label by name.
    """
    if JeevesLib.doesLabelExist(label_name):
        return JeevesLib.getLabel(label_name)
    else:
        label = JeevesLib.mkLabel(label_name, uniquify=False)
        model_name, field_name, jeeves_id = label_name.split('__')
        model = get_model(app_label, model_name)
        # TODO: optimization: most of the time this obj will be the one we are
        # already fetching
        obj = model.objects.get(use_base_env=True, jeeves_id=jeeves_id)
        restrictor = getattr(model, 'jeeves_restrict_' + field_name)
        JeevesLib.restrict(label, lambda ctxt: restrictor(obj, ctxt), True)
        return label

def get_one_differing_var(vars1, vars2):
    """Checks to see if two sets of variables have one differing one??
    """
    if len(vars1) != len(vars2):
        return None
    ans = None
    for var in vars1:
        if var in vars2:
            if vars1[var] != vars2[var]:
                if ans is None:
                    ans = var
                else:
                    return None
        else:
            return None
    return ans

def label_for(*field_names):
    """The decorator for associating a label with a field.
    """
    def decorator(field):
        """Definition of the decorator itself.
        """
        field._jeeves_label_for = field_names
        return field
    return decorator

#from django.db.models.base import ModelBase
#class JeevesModelBase(ModelBase):
#  def __new__(cls, name, bases, attrs):
#    obj = super(ModelBase, cls).__new__(cls, name, bases, attrs)

#    return obj

# Make a Jeeves Model that enhances the vanilla Django model with information
# about how labels work and that kind of thing. We'll also need to override
# some methods so that we can create records and make queries appropriately.

class JeevesModel(models.Model):
    """ Jeeves version of Django's Model class.
    """

    def __init__(self, *args, **kw):
        self.jeeves_base_env = JeevesLib.jeevesState.pathenv.getEnv()
        super(JeevesModel, self).__init__(*args, **kw)

        self._jeeves_labels = {}
        field_names = [f.name for f in self._meta.concrete_fields]
        for attr in dir(self.__class__):
            if attr.startswith('jeeves_restrict_'):
                value = getattr(self.__class__, attr)
                label_name = attr[len('jeeves_restrict_'):]
                assert label_name not in self._jeeves_labels
                if hasattr(value, '_jeeves_label_for'):
                    self._jeeves_labels[label_name] = value._jeeves_label_for
                else:
                    assert label_name in field_names
                    self._jeeves_labels[label_name] = (label_name,)

    def __setattr__(self, name, value):
        field_names = [field.name for field in self._meta.concrete_fields] \
                        if hasattr(self, '_meta') else []
        if name in field_names and \
            name not in ('jeeves_vars', 'jeeves_id', 'id'):
            old_val = getattr(self, name) if hasattr(self, name) else \
                        Unassigned("attribute '%s' in %s" % \
                            (name, self.__class__.__name__))
            models.Model.__setattr__(
                self, name, JeevesLib.jassign(
                    old_val, value, self.jeeves_base_env))
        else:
            models.Model.__setattr__(self, name, value)

    objects = JeevesManager()
    jeeves_id = CharField(max_length=JeevesModelUtils.JEEVES_ID_LEN, null=False)
    jeeves_vars = CharField(max_length=1024, null=False)

    @JeevesLib.supports_jeeves
    def do_delete(self, vars_env):
        """A helper for delete?
        """
        if len(vars_env) == 0:
            delete_query = self.__class__._objects_ordinary.filter(
                            jeeves_id=self.jeeves_id)
            delete_query.delete()
        else:
            filter_query = self.__class__._objects_ordinary.filter(
                            jeeves_id=self.jeeves_id)
            objs = list(filter_query)
            for obj in objs:
                eobj = JeevesModelUtils.unserialize_vars(obj.jeeves_vars)
                if any(var_name in eobj and eobj[var_name] != var_value
                        for var_name, var_value in vars_env.iteritems()):
                    continue
                if all(var_name in eobj and eobj[var_name] == var_value
                        for var_name, var_value in vars_env.iteritems()):
                    super(JeevesModel, obj).delete()
                    continue
                addon = ""
                for var_name, var_value in vars_env.iteritems():
                    if var_name not in eobj:
                        new_obj = clone(obj)
                        if addon != "":
                            new_obj.id = None
                            # so when we save a new row will be made
                        new_obj.jeeves_vars += addon + '%s=%d;' \
                                                    % (var_name, not var_value)
                        addon += '%s=%d;' % (var_name, var_value)
                        super(JeevesModel, new_obj).save()

    @JeevesLib.supports_jeeves
    def acquire_label(self, field_name):
        label_name = '%s__%s__%s' % \
                        (self.__class__.__name__, field_name, self.jeeves_id)
        if JeevesLib.doesLabelExist(label_name):
            return JeevesLib.getLabel(label_name)
        else:
            label = JeevesLib.mkLabel(label_name, uniquify=False)
            restrictor = getattr(self, 'jeeves_restrict_' + field_name)
            JeevesLib.restrict(label
                , lambda ctxt: restrictor(self, ctxt), True)
            return label

    @JeevesLib.supports_jeeves
    def save(self, *args, **kw):
        """Saves elements with the appropriate faceted labels.
        """
        def full_eval(val, env):
            """Evaluating a value in the context of an environment.
            """
            eval_expr = val.partialEval(env)
            return eval_expr.v

        # TODO: OMG why is this so long.
        if not self.jeeves_id:
            self.jeeves_id = JeevesModelUtils.get_random_jeeves_id()

        if kw.get("update_field", None) is not None:
            raise NotImplementedError("Partial saves not supported.")

        # Go through fields and do something. TODO: Figure out what.
        field_names = set()
        for field in self._meta.concrete_fields:
            if not field.primary_key and not hasattr(field, 'through'):
                field_names.add(field.attname)

        # Go through labels and create facets.
        for label_name, field_name_list in self._jeeves_labels.iteritems():
            label = self.acquire_label(label_name)
            for field_name in field_name_list:
                public_field_value = getattr(self, field_name)
                private_field_value = getattr(self
                                        , 'jeeves_get_private_' + \
                                            field_name)(self)
                print "WE GET HERE"
                faceted_field_value = JeevesLib.mkSensitive(label
                                        , public_field_value
                                        , private_field_value).partialEval(
                                            JeevesLib.jeevesState.pathenv. \
                                                getEnv())
                setattr(self, field_name, faceted_field_value)

        all_vars = []
        field_dict = {}
        env = JeevesLib.jeevesState.pathenv.getEnv()
        for field_name in field_names:
            value = getattr(self, field_name)
            field_val = fexpr_cast(value).partialEval(env)
            all_vars.extend(v.name for v in field_val.vars())
            field_dict[field_name] = field_val
        all_vars = list(set(all_vars))

        for cur_vars in JeevesModelUtils.powerset(all_vars):
            true_vars = list(cur_vars)
            false_vars = list(set(all_vars).difference(cur_vars))
            env_dict = dict(env)
            env_dict.update({tv : True for tv in true_vars})
            env_dict.update({fv : False for fv in false_vars})

            self.do_delete(env_dict)

            klass = self.__class__
            obj_to_save = klass(**{
                field_name : full_eval(field_value, env_dict)
                for field_name, field_value in field_dict.iteritems()
            })

            all_jid_objs = list(
                            klass._objects_ordinary.filter(
                                jeeves_id=obj_to_save.jeeves_id).all())
            all_relevant_objs = [obj for obj in all_jid_objs if
                all(field_name == 'jeeves_vars' or
                    getattr(obj_to_save, field_name) == getattr(obj, field_name)
                    for field_name in field_dict)]

            # Optimization.
            # TODO: See how we can refactor this to shorten the function.
            while True:
                # check if we can collapse
                # if we can, repeat; otherwise, exit
                for i in xrange(len(all_relevant_objs)):
                    other_obj = all_relevant_objs[i]
                    diff_var = get_one_differing_var(env_dict
                                , JeevesModelUtils.unserialize_vars(
                                    other_obj.jeeves_vars))
                    if diff_var is not None:
                        super(JeevesModel, other_obj).delete()
                        del env_dict[diff_var]
                        break
                else:
                    break

            obj_to_save.jeeves_vars = JeevesModelUtils.serialize_vars(env_dict)
            super(JeevesModel, obj_to_save).save(*args, **kw)

    @JeevesLib.supports_jeeves
    def delete(self):
        if self.jeeves_id is None:
            return

        field_names = set()
        for field in self._meta.concrete_fields:
            if not field.primary_key and not hasattr(field, 'through'):
                field_names.add(field.attname)

        all_vars = []
        field_dict = {}
        env = JeevesLib.jeevesState.pathenv.getEnv()
        for field_name in field_names:
            value = getattr(self, field_name)
            field_fexpr = fexpr_cast(value).partialEval(env)
            all_vars.extend(v.name for v in field_fexpr.vars())
            field_dict[field_name] = field_fexpr

        for var_set in JeevesModelUtils.powerset(all_vars):
            true_vars = list(var_set)
            false_vars = list(set(all_vars).difference(var_set))
            env_dict = dict(env)
            env_dict.update({tv : True for tv in true_vars})
            env_dict.update({fv : False for fv in false_vars})

            self.do_delete(env_dict)

    class Meta(object):
        """Abstract class.
        """
        abstract = True

    _objects_ordinary = Manager()

    @JeevesLib.supports_jeeves
    def __eq__(self, other):
        if isinstance(other, FExpr):
            return other == self
        return isinstance(other, self.__class__) and \
            self.jeeves_id == other.jeeves_id

    @JeevesLib.supports_jeeves
    def __ne__(self, other):
        if isinstance(other, FExpr):
            return other != self
        return not (isinstance(other, self.__class__) and \
            self.jeeves_id == other.jeeves_id)

from django.contrib.auth.models import User
@JeevesLib.supports_jeeves
def evil_hack(self, other):
    """Hack __eq__ that checks equality if we have FExprs and checks object ID
    equality otherwise.
    """
    if isinstance(other, FExpr):
        return other == self
    return isinstance(other, self.__class__) and self.id == other.id
User.__eq__ = evil_hack

class JeevesRelatedObjectDescriptor(property):
    """WRITE SOME COMMENTS.
    """
    @JeevesLib.supports_jeeves
    def __init__(self, field):
        self.field = field
        self.cache_name = field.get_cache_name()

    @JeevesLib.supports_jeeves
    def get_cache(self, instance):
        """Gets the... cache?
        """
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

    @JeevesLib.supports_jeeves
    def __get__(self, instance, instance_type):
        """??
        """
        if instance is None:
            return self

        cache = self.get_cache(instance)
        def get_obj(jeeves_id):
            """??
            """
            if jeeves_id is None:
                return None
            if jeeves_id not in cache:
                cache[jeeves_id] = self.field.to.objects.get(
                                    **{self.field.join_field.name:jeeves_id})
            return cache[jeeves_id]
        if instance is None:
            return self
        return JeevesLib.facetMapper(
                fexpr_cast(
                    getattr(instance, self.field.get_attname())), get_obj)

    @JeevesLib.supports_jeeves
    def __set__(self, instance, value):
        cache = self.get_cache(instance)
        def get_id(obj):
            """Gets the ID associated with an object.
            """
            if obj is None:
                return None
            obj_jid = getattr(obj, self.field.join_field.name)
            if obj_jid is None:
                raise Exception("Object must be saved before it can be \
                    attached via JeevesForeignKey.")
            cache[obj_jid] = obj
            return obj_jid
        ids = JeevesLib.facetMapper(fexpr_cast(value), get_id)
        setattr(instance, self.field.get_attname(), ids)

from django.db.models.fields.related import ForeignObject
class JeevesForeignKey(ForeignObject):
    """Jeeves version of Django's ForeignKey.
    """
    requires_unique_target = False
    @JeevesLib.supports_jeeves
    def __init__(self, to, *args, **kwargs):
        self.to = to

        for field in self.to._meta.fields:
            if field.name == 'jeeves_id':
                self.join_field = field
                break
            else:
                # support non-Jeeves tables
                self.join_field = to._meta.pk
                #raise Exception("Need jeeves_id field")

        kwargs['on_delete'] = models.DO_NOTHING
        super(JeevesForeignKey, self).__init__(
            to, [self], [self.join_field], *args, **kwargs)
        self.db_constraint = False

    @JeevesLib.supports_jeeves
    def contribute_to_class(self, cls, name, virtual_only=False):
        super(JeevesForeignKey, self).contribute_to_class(
            cls, name, virtual_only=virtual_only)
        setattr(cls, self.name, JeevesRelatedObjectDescriptor(self))

    @JeevesLib.supports_jeeves
    def get_attname(self):
        return '%s_id' % self.name

    @JeevesLib.supports_jeeves
    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or attname
        return attname, column

    '''
    @JeevesLib.supports_jeeves
    def db_type(self, connection):
        return IntegerField().db_type(connection=connection)
    '''

    @JeevesLib.supports_jeeves
    def get_path_info(self):
        opts = self.to._meta
        from_opts = self.model._meta
        return [django.db.models.fields.related.PathInfo(
                    from_opts, opts, (self.join_field,), self, False, True)]

    @JeevesLib.supports_jeeves
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

    @JeevesLib.supports_jeeves
    def get_extra_restriction(self, where_class, alias, related_alias):
        return None

    @JeevesLib.supports_jeeves
    def get_cache_name(self):
        return '_jfkey_cache_' + self.name

    def db_type(self, connection):
        return "VARCHAR(%d)" % JeevesModelUtils.JEEVES_ID_LEN
