"""API for Python Jeeves libary.

    :synopsis: Functions for creating sensitive values, labels, and policies.

.. moduleauthor:: Travis Hance <tjhance7@gmail.com>
.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>

"""

from env.ConcreteCache import ConcreteCache
from env.VarEnv import VarEnv
from env.PolicyEnv import PolicyEnv
from env.PathVars import PathVars
from env.WritePolicyEnv import WritePolicyEnv
from smt.Z3 import Z3
from fast.AST import Facet, fexpr_cast, Constant, Var, Not, FExpr, Unassigned, FObject, jeevesState
import copy

def set_log_policies(filehandle):
    """
    Set policy logging.
    """
    jeevesState.set_log_policies(filehandle)
def log_policies():
    """
    Write policies to the policy files.
    """
    jeevesState.log_policies()
def log_counts(label_count):
    jeevesState.log_counts(label_count)
def clear_policy_count():
    jeevesState.clear_policy_count()
def get_num_concretize():
    return jeevesState.num_concretize
def get_num_concretize_labels():
    return jeevesState.num_labels
def get_num_env_labels():
    return len(jeevesState.policyenv.policies.keys())

def init():
    """Initialization function for Jeeves library.

    You should always call this before you do anything Jeeves-y.

    """
    jeevesState.init()

    # TODO this needs to be GC'ed somehow

def supports_jeeves(f):
    f.__jeeves = 0
    return f

@supports_jeeves
def mkLabel(varName = "", uniquify=True):
    """Makes a label to associate with policies and sensitive values.

    :param varName: Optional variable name (to help with debugging).
    :type varName: string
    :returns: Var - fresh label.
    """
    label = jeevesState.policyenv.mkLabel(varName, uniquify)
    jeevesState.all_labels[label.name] = label
    return label

@supports_jeeves
def doesLabelExist(varName):
    return varName in jeevesState.all_labels

@supports_jeeves
def getLabel(varName):
    return jeevesState.all_labels[varName]

@supports_jeeves
def restrict(varLabel, pred, use_empty_env=False):
    """Associates a policy with a label.

    :param varLabel: Label to associate with policy.
    :type varLabel: string
    :param pred: Policy: function taking output channel and returning Boolean result.
    :type pred: T -> bool, where T is the type of the output channel
    """
    jeevesState.policyenv.restrict(varLabel, pred, use_empty_env)

@supports_jeeves
def mkSensitive(varLabel, vHigh, vLow):
    """Creates a sensitive value with two facets.

    :param varLabel: Label to associate with sensitive value.
    :type varLabel: Var
    :param vHigh: High-confidentiality facet for viewers with restricted access.
    :type vHigh: T
    :param vLow: Low-confidentiality facet for other viewers.
    :type vLow: T
    """

    if isinstance(varLabel, Var):
        return Facet(varLabel, fexpr_cast(vHigh), fexpr_cast(vLow))
    else:
        return JeevesLib.jif(varLabel, lambda:vHigh, lambda:vLow)

@supports_jeeves
def concretize(ctxt, v):
    """Projects out a single value to the viewer.

    :param ctxt: Output channel (viewer).
    :type ctxt: T, where policies have type T -> bool
    :param v: Value to concretize.
    :type v: FExpr
    :returns: The concrete (non-faceted) version of T under the policies in the environment.
    """
    pathvars = jeevesState.pathenv.getEnv()
    # Check to see if the value is in the cache.
    cache_key = jeevesState.concretecache.get_cache_key(ctxt, v, pathvars)
    cval = jeevesState.concretecache.cache_lookup(cache_key)
    if cval is None:
        # If not, then concretize anew and cache the value.
        cval = jeevesState.policyenv.concretizeExp(ctxt, v, pathvars)
        jeevesState.concretecache.cache_value(cache_key, cval)
    return cval

@supports_jeeves
def assignLabel(ctxt, label):
    pathvars = jeevesState.pathenv.getEnv()
    return jeevesState.policyenv.assignLabel(jeevesState.solverstate
        , label, pathvars)

@supports_jeeves
def jif(cond, thn_fn, els_fn):
    condTrans = fexpr_cast(cond).partialEval(jeevesState.pathenv.getEnv())
    if condTrans.type != bool:
        raise TypeError("jif must take a boolean as a condition")
    return jif2(condTrans, thn_fn, els_fn)

def jif2(cond, thn_fn, els_fn):
        if isinstance(cond, Constant):
                return thn_fn() if cond.v else els_fn()
        elif isinstance(cond, Facet):
                if not isinstance(cond.cond, Var):
                        raise TypeError("facet conditional is of type %s"                                                                        % cond.cond.__class__.__name__)
                with PositiveVariable(cond.cond):
                        thn = jif2(cond.thn, thn_fn, els_fn)
                with NegativeVariable(cond.cond):
                        els = jif2(cond.els, thn_fn, els_fn)
                return Facet(cond.cond, thn, els)
        else:
                raise TypeError("jif condition must be a constant or a var")

# supports short-circuiting
# without short-circuiting jif is unnecessary
# are there performance issues?
@supports_jeeves
def jand(l, r): # inputs are functions
        left = l()
        if not isinstance(left, FExpr):
                return left and r()
        return jif(left, r, lambda:left)

@supports_jeeves
def jor(l, r): # inputs are functions
        left = l()
        if not isinstance(left, FExpr):
                return left or r()
        return jif(left, lambda:left, r)

# this one is more straightforward
# just takes an expression
@supports_jeeves
def jnot(f):
        if isinstance(f, FExpr):
                return Not(f)
        else:
                return not f

@supports_jeeves
def jassign(old, new, base_env={}):
    res = new
    for vs in jeevesState.pathenv.conditions:
        (var, val) = (vs.var, vs.val)
        if var.name not in base_env:
            if val:
                res = Facet(var, res, old)
            else:
                res = Facet(var, old, res)
    if isinstance(res, FExpr):
        return res.partialEval({}, True)
    else:
        return res

'''
Caching.
'''
def start_caching():
    jeevesState.concretecache.start_caching()
def stop_caching():
    jeevesState.concretecache.stop_caching()
def cache_size():
    return jeevesState.concretecache.cache_size()
def clear_cache():
    return jeevesState.concretecache.clear_cache()
def get_cache():
    return jeevesState.concretecache.cache

def get_solverstate():
    return jeevesState.solverstate

'''
Early concretization optimization.
'''
def set_viewer(viewer):
    jeevesState.set_viewer(viewer)
    jeevesState.reset_solverstate(viewer)
def reset_viewer(viewer):
    jeevesState.reset_viewer()
    jeevesState.clear_solverstate()
def get_viewer():
    return jeevesState.viewer

class PositiveVariable:
    def __init__(self, var):
        self.var = var
    def __enter__(self):
        jeevesState.pathenv.push(self.var, True)
    def __exit__(self, type, value, traceback):
        jeevesState.pathenv.pop()

class NegativeVariable:
    def __init__(self, var):
        self.var = var
    def __enter__(self):
        jeevesState.pathenv.push(self.var, False)
    def __exit__(self, type, value, traceback):
        jeevesState.pathenv.pop()

def liftTuple(t):
        t = fexpr_cast(t)
        if isinstance(t, FObject):
                return t.v
        elif isinstance(t, Facet):
                a = liftTuple(t.thn)
                b = liftTuple(t.els)
                return tuple([Facet(t.cond, a1, b1) for (a1, b1) in zip(a, b)])
        else:
                raise TypeError("bad use of liftTuple")

class Namespace:
        def __init__(self, kw, funcname):
                self.__dict__.update(kw)
                self.__dict__['_jeeves_funcname'] = funcname
                self.__dict__['_jeeves_base_env'] = jeevesState.pathenv.getEnv()

        def __setattr__(self, attr, value):
                self.__dict__[attr] = jassign(self.__dict__.get(
                                                                attr, Unassigned("variable '%s' in %s" % \
                                                                        (attr, self._jeeves_funcname)))
                                                                , value, self.__dict__['_jeeves_base_env'])

@supports_jeeves
def jgetattr(obj, attr):
        if isinstance(obj, FExpr):
                return getattr(obj, attr)
        else:
                return getattr(obj, attr) if hasattr(obj, attr) else Unassigned("attribute '%s'" % attr)

@supports_jeeves
def jgetitem(obj, item):
        try:
                return obj[item]
        except (KeyError, KeyError, TypeError) as e:
                return Unassigned("item '%s'" % attr)

@supports_jeeves
def jmap(iterable, mapper):
        if isinstance(iterable, JList2):
                return jmap_jlist2(iterable, mapper)
        if isinstance(iterable, FObject) and isinstance(iterable.v, JList2):
                return jmap_jlist2(iterable.v, mapper)

        iterable = fexpr_cast(iterable).partialEval(jeevesState.pathenv.getEnv())
        return FObject(JList(jmap2(iterable, mapper)))
def jmap2(iterator, mapper):
        if isinstance(iterator, Facet):
                if jeevesState.pathenv.hasPosVar(iterator.cond):
                        return jmap2(iterator.thn, mapper)
                if jeevesState.pathenv.hasNegVar(iterator.cond):
                        return jmap2(iterator.els, mapper)
                with PositiveVariable(iterator.cond):
                        thn = jmap2(iterator.thn, mapper)
                with NegativeVariable(iterator.cond):
                        els = jmap2(iterator.els, mapper)
                return Facet(iterator.cond, thn, els)
        elif isinstance(iterator, FObject):
                return jmap2(iterator.v, mapper)
        elif isinstance(iterator, JList):
                return jmap2(iterator.l, mapper)
        elif isinstance(iterator, JList2):
                return jmap2(iterator.convert_to_jlist1().l, mapper)
        elif isinstance(iterator, list) or isinstance(iterator, tuple):
                return FObject([mapper(item) for item in iterator])
        else:
                return jmap2(iterator.__iter__(), mapper)

def jmap_jlist2(jlist2, mapper):
        ans = JList2([])
        env = jeevesState.pathenv.getEnv()
        for i, e in jlist2.l:
                popcount = 0
                for vname, vval in e.iteritems():
                        if vname not in env:
                                v = getLabel(vname)
                                jeevesState.pathenv.push(v, vval)
                                popcount += 1
                        elif env[vname] != vval:
                                break
                        ans.l.append((mapper(i), e))
                for _ in xrange(popcount):
                        jeevesState.pathenv.pop()
        return FObject(ans)

def facetMapper(facet, fn, wrapper=fexpr_cast):
        if isinstance(facet, Facet):
                return Facet(facet.cond, facetMapper(facet.thn, fn, wrapper)
                        , facetMapper(facet.els, fn, wrapper))
        elif isinstance(facet, Constant) or isinstance(facet, FObject):
                return wrapper(fn(facet.v))

class JList:
    def validate(self):
        def foo(x):
            assert isinstance(x, list), 'thingy is ' + str(x.l.v)
            return x
        facetMapper(self.l, foo, lambda x : x)

    def __init__(self, l):
        self.l = l if isinstance(l, FExpr) else FObject(l)
        self.validate()
    def __getitem__(self, i):
        return self.l[i]
    def __setitem__(self, i, val):
        self.l[i] = jassign(self.l[i], val)

    def __len__(self):
        return self.l.__len__()
    def __iter__(self):
        return self.l.__iter__()

    def append(self, val):
        l2 = facetMapper(self.l, list, FObject) #deep copy
        l2.append(val)
        self.l = jassign(self.l, l2)
        self.validate()

    def prettyPrint(self):
        def tryPrint(x):
            return x.__class__.__name__
            '''
            try:
                return x.__class__.__name__ #x.prettyPrint()
            except AttributeError:
                return str(x)
            '''
        return str(len(self.l)) #''.join(map(tryPrint, self.l))

class JList2:
        def __init__(self, l=[]):
                if isinstance(l, list):
                        self.l = [(i, {}) for i in l]
                else:
                        raise NotImplementedError
                
        def append(self, val):
                self.l.append((val, jeevesState.pathenv.getEnv()))

        def eval(self, env):
                return [i for i,e in self.l if all(env[getLabel(v)] == e[v] for v in e)]

        def vars(self):
                all_vars = set()
                for _, e in self.l:
                        all_vars.update(set(e.keys()))
                return {getLabel(v) for v in all_vars}

        def convert_to_jlist1(self):
                all_vars = [v.name for v in self.vars()]
                def rec(cur_e, i):
                        if i == len(all_vars):
                                return FObject(
                                        [i for i,e in self.l if all(cur_e[v] == e[v] for v in e)])
                        else:
                                cur_e1 = dict(cur_e)
                                cur_e2 = dict(cur_e)
                                cur_e1[all_vars[i]] = True
                                cur_e2[all_vars[i]] = False
                                return Facet(getLabel(all_vars[i]),
                                        rec(cur_e1, i+1), rec(cur_e2, i+1))
                return JList(rec({}, 0))

        def __getitem__(self, i):
                return self.convert_to_jlist1().__getitem__(i)

        def __setitem__(self, i, val):
                raise NotImplementedError

        def __len__(self):
                return self.convert_to_jlist1().__len__()

class JIterator:
        def __init__(self, l):
                self.l = l

@supports_jeeves
def jfun(f, *args, **kw):
        if hasattr(f, '__jeeves'):
                return f(*args, **kw)
        else:
                env = jeevesState.pathenv.getEnv()
                if len(args) > 0:
                        return jfun2(
                                f, args, kw, 0, fexpr_cast(args[0]).partialEval(env), [])
                else:
                        it = kw.__iter__()
                        try:
                                fst = next(it)
                        except StopIteration:
                                return fexpr_cast(f())
                        return jfun3(
                                f, kw, it, fst, fexpr_cast(kw[fst]).partialEval(env), (), {})

def jfun2(f, args, kw, i, arg, args_concrete):
        if isinstance(arg, Constant) or isinstance(arg, FObject):
                env = jeevesState.pathenv.getEnv()
                if i < len(args) - 1:
                        return jfun2(f, args, kw, i+1
                                , fexpr_cast(args[i+1]).partialEval(env)
                                , tuple(list(args_concrete) + [arg.v]))
                else:
                        it = kw.__iter__()
                        try:
                                fst = next(it)
                        except StopIteration:
                                return fexpr_cast(f(*tuple(list(args_concrete) + [arg.v])))
                        return jfun3(f, kw, it, fst, fexpr_cast(kw[fst]).partialEval(env)
                                , tuple(list(args_concrete) + [arg.v]), {})
        else:
                with PositiveVariable(arg.cond):
                        thn = jfun2(f, args, kw, i, arg.thn, args_concrete)
                with NegativeVariable(arg.cond):
                        els = jfun2(f, args, kw, i, arg.els, args_concrete)
                return Facet(arg.cond, thn, els)

from itertools import tee
def jfun3(f, kw, it, key, val, args_concrete, kw_concrete):
                if isinstance(val, Constant) or isinstance(val, FObject):
                                kw_c = dict(kw_concrete)
                                kw_c[key] = val.v
                                try:
                                                next_key = next(it)
                                except StopIteration:
                                                return fexpr_cast(f(*args_concrete, **kw_c))
                                env = jeevesState.pathenv.getEnv()
                                return jfun3(f, kw, it, next_key
                                                , fexpr_cast(kw[next_key]).partialEval(env), args_concrete, kw_c)
                else:
                                it1, it2 = tee(it)
                                with PositiveVariable(val.cond):
                                                thn = jfun3(f, kw, it1, key, val.thn, args_concrete, kw_concrete)
                                with NegativeVariable(val.cond):
                                                els = jfun3(f, kw, it2, key, val.els, args_concrete, kw_concrete)
                                return Facet(val.cond, thn, els)

def evalToConcrete(f):
    g = fexpr_cast(f).partialEval(jeevesState.pathenv.getEnv())
    if isinstance(g, Constant):
        return g.v
    elif isinstance(g, FObject):
        return g.v
    else:
        raise Exception("wow such error: evalToConcrete on non-concrete thingy-ma-bob")

'''
TODO
def recursiveEvalToConcrete(f):
    """
    Evaluates the fields of an object to be concrete.
    """
    g = fexpr_cast(f).partialEval(jeevesState.pathenv.getEnv()
'''

from jlib.JContainer import *
