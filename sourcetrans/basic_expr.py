from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

import common

"""
Transforms all expressions in a tree if they are not overidable normally
For example, and -> jand
not -> jnot
A if CONDITION else B -> jif
"""

def basic_expr_transform(node):
  @Walker
  def transform(tree, stop, **kw):
    # not expr
    # JeevesLib.jnot(expr)
    if isinstance(tree, UnaryOp) and isinstance(tree.op, Not):
      return q[ JeevesLib.jnot(ast[tree.operand]) ]

    # a1 and a2 and ... and an
    # JeevesLib.jand(lambda : left, lambda : right)
    if isinstance(tree, BoolOp):
      if isinstance(tree.op, And):
        fn = q[ JeevesLib.jand ]
      else:
        fn = q[ JeevesLib.jor ]
      result = tree.values[-1]
      for operand in tree.values[-2::-1]:
        result = q[ ast[fn](lambda : ast[operand], lambda : ast[result]) ]
      return result

    if isinstance(tree, List):
      elts = [transform.recurse(elt) for elt in tree.elts]
      newlist = List(elts=elts, ctx=tree.ctx)
      stop()
      return q[ JeevesLib.JList(ast[newlist]) ]

    # thn if cond else els
    # JeevesLib.jif(cond, lambda : thn, lambda : els)
    if isinstance(tree, IfExp):
      return q[ JeevesLib.jif(ast[tree.test], lambda : ast[tree.body], lambda : ast[tree.orelse]) ]

    # [expr for args in iterator]
    # JeevesLib.jmap(iterator
    if isinstance(tree, ListComp):
      elt = tree.elt
      generators = tree.generators
      assert len(generators) == 1
      assert len(generators[0].ifs) == 0
      target = common.storeToParam(generators[0].target)
      iter = generators[0].iter
      lmbda = Lambda(
        args=arguments(
          args=[target],
          vararg=None,
          kwarg=None,
          defaults=[]
        ),
        body=elt
      )
      return q[ JeevesLib.jmap(ast[iter], ast[lmbda]) ]

    if isinstance(tree, Compare):
      assert len(tree.ops) == 1
      # TODO other comparisons besides 'in'
      if isinstance(tree.ops[0], In):
        return q[ JeevesLib.jhas(ast[tree.comparators[0]], ast[tree.left]) ]

  return transform.recurse(node)
