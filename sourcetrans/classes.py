
from macropy.core.macros import *
from macropy.core.quotes import macros, ast, u
from ast import *

def classes_transform(node, gen_sym):

    @Walker
    def transform(tree, **k2):
        if isinstance(tree, ClassDef):
            self_name = gen_sym()
            attr_name = gen_sym()
            value_name = gen_sym()
            newfunc = FunctionDef(name='__setattr__', args=arguments(args=[Name(id=self_name, ctx=Param()), Name(id=attr_name, ctx=Param()), Name(id=value_name, ctx=Param())], vararg=None, kwarg=None, defaults=[]), decorator_list=[], body=[Assign([Subscript(value=Attribute(value=Name(id=self_name, ctx=Load()), attr='__dict__', ctx=Load()), slice=Index(Name(id=attr_name, ctx=Load())), ctx=Store())], Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='jassign', ctx=Load()), args=[Call(func=Attribute(value=Attribute(value=Name(id=self_name), attr='__dict__', ctx=Load()), attr='get', ctx=Load()), args=[Name(id=attr_name), Call(func=Attribute(value=Name(id='JeevesLib', ctx=Load()), attr='Unassigned', ctx=Load()), args=[BinOp(left=Str(s="attribute '%s'"), op=Mod(), right=Name(id=attr_name))], keywords=[], starargs=None, kwargs=None)], keywords=[], starargs=None, kwargs=None), Name(id=value_name)], keywords=[], starargs=None, kwargs=None))])
            return copy_location(ClassDef(name=tree.name, bases=tree.bases, body=([newfunc] + tree.body), decorator_list=tree.decorator_list), tree)
    return transform.recurse(node)