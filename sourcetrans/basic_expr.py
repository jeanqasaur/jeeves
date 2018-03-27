
from macropy.core.macros import *
from macropy.core.quotes import macros, ast, u
from ast import *
import common
'\nTransforms all expressions in a tree if they are not overidable normally\nFor example, and -> jand\nnot -> jnot\nA if CONDITION else B -> jif\n'

def basic_expr_transform(node):

    @Walker
    def transform(tree, stop, **kw):
        if (isinstance(tree, FunctionDef) or isinstance(tree, ClassDef)):
            for decorator in tree.decorator_list:
                if (isinstance(decorator, Name) and (decorator.id == 'jeeves')):
                    raise Exception('Do not use nested @jeeves')
        if (isinstance(tree, UnaryOp) and isinstance(tree.op, Not)):
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jnot', ctx=Load()), args=[tree.operand], keywords=[], starargs=None, kwargs=None)
        if isinstance(tree, BoolOp):
            if isinstance(tree.op, And):
                fn = Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jand', ctx=Load())
            else:
                fn = Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jor', ctx=Load())
            result = tree.values[(-1)]
            for operand in tree.values[(-2)::(-1)]:
                result = Call(func=fn, args=[Lambda(args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), body=operand), Lambda(args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), body=result)], keywords=[], starargs=None, kwargs=None)
            return result
        if isinstance(tree, List):
            elts = [transform.recurse(elt) for elt in tree.elts]
            newlist = List(elts=elts, ctx=tree.ctx)
            stop()
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='JList', ctx=Load()), args=[newlist], keywords=[], starargs=None, kwargs=None)
        if isinstance(tree, IfExp):
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jif', ctx=Load()), args=[tree.test, Lambda(args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), body=tree.body), Lambda(args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), body=tree.orelse)], keywords=[], starargs=None, kwargs=None)
        if isinstance(tree, ListComp):
            elt = tree.elt
            generators = tree.generators
            assert (len(generators) == 1)
            assert (len(generators[0].ifs) == 0)
            target = common.storeToParam(generators[0].target)
            iter = generators[0].iter
            lmbda = Lambda(args=arguments(args=[target], vararg=None, kwarg=None, defaults=[]), body=elt)
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jmap', ctx=Load()), args=[iter, lmbda], keywords=[], starargs=None, kwargs=None)
        if isinstance(tree, Compare):
            assert (len(tree.ops) == 1)
            if isinstance(tree.ops[0], In):
                return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jhas', ctx=Load()), args=[tree.comparators[0], tree.left], keywords=[], starargs=None, kwargs=None)
        if isinstance(tree, Call):
            func = transform.recurse(tree.func)
            args = [transform.recurse(arg) for arg in tree.args]
            keywords = [transform.recurse(kw) for kw in tree.keywords]
            starargs = transform.recurse(tree.starargs)
            kwargs = transform.recurse(tree.kwargs)
            stop()
            return Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jfun', ctx=Load()), args=([func] + args), keywords=keywords, starargs=starargs, kwargs=kwargs)
    return transform.recurse(node)