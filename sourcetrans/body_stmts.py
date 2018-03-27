
from macropy.core.macros import *
from macropy.core.quotes import macros, ast, u
from ast import *
import common
import copy
'\nReplace if-statments and for-blocks with jif and jmap\n'

def body_stmts_transform(tree, gen_sym):

    @Walker
    def transform(tree, stop, **kw):
        if isinstance(tree, If):
            thn_fn_name = gen_sym()
            els_fn_name = gen_sym()
            test = transform.recurse(tree.test)
            thn_body = transform.recurse(tree.body)
            els_body = transform.recurse(tree.orelse)
            stop()

            def get_func(funcname, funcbody):
                return FunctionDef(name=funcname, args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), body=(funcbody or [Pass()]), decorator_list=[])
            return [get_func(thn_fn_name, thn_body), get_func(els_fn_name, els_body), Expr(value=Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jif', ctx=Load()), args=[test, Name(id=thn_fn_name, ctx=Load()), Name(id=els_fn_name, ctx=Load())], keywords=[], starargs=None, kwargs=None))]
        if isinstance(tree, For):
            body_fn_name = gen_sym()
            iter = transform.recurse(tree.iter)
            body = transform.recurse(tree.body)
            targetParams = common.storeToParam(copy.deepcopy(tree.target))
            assert ((len(tree.orelse) == 0) or isinstance(tree.orelse[0], Pass))
            stop()
            func = copy_location(FunctionDef(name=body_fn_name, args=arguments(args=[targetParams], vararg=None, kwarg=None, defaults=[]), body=body, decorator_list=[]), tree)
            return [func, Expr(value=Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jmap', ctx=Load()), args=[iter, Name(body_fn_name, Load())], keywords=[], starargs=None, kwargs=None))]
    return transform.recurse(tree)