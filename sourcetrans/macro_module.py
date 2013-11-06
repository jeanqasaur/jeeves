# macro_module.py
from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

from basic_expr import basic_expr_transform
from body_stmts import body_stmts_transform
from namespace import replace_local_scopes_with_namespace
from classes import classes_transform

macros = Macros()

@macros.decorator
def jeeves(tree, gen_sym, **kw):
    tree = basic_expr_transform(tree)
    tree = replace_local_scopes_with_namespace(tree, gen_sym)
    tree = body_stmts_transform(tree, gen_sym)

    tree = classes_transform(tree, gen_sym)

    return tree
