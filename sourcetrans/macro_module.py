# macro_module.py
from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

macros = Macros()

def get_vars_in_scope(node):
  @Walker
  def get_vars(tree, collect, stop, **kw):
    if isinstance(tree, Name) and isinstance(tree.ctx, Store):
      collect(tree.id)
    if tree != node and (isinstance(tree, ClassDef) or isinstance(tree, FunctionDef)):
      stop()

  @Walker
  def get_globals(tree, collect, stop, **kw):
    if isinstance(tree, Global):
      for name in tree.names:
        collect(name)
    if tree != node and (isinstance(tree, ClassDef) or isinstance(tree, FunctionDef)):
      stop()

  _, v = get_vars.recurse_collect(node)
  _, g = get_globals.recurse_collect(node)
  return list(set(v) - set(g))

@macros.decorator
def jeeves(tree, **kw):
  @Walker
  def transform(tree, stop, **kw):
    # not expr
    # JeevesLib.jnot(expr)
    if isinstance(tree, UnaryOp) and isinstance(tree.op, Not):
      return q[ JeevesLib.jnot(ast[tree.operand]) ]

    # left and right
    # JeevesLib.jand(lambda : left, lambda : right)
    if isinstance(tree, BoolOp) and isinstance(tree.op, And):
      return q[ JeevesLib.jand(ast[tree.left], ast[tree.right]) ]

    # left or right
    # JeevesLib.jor(lambda : left, lambda : right)
    if isinstance(tree, BoolOp) and isinstance(tree.op, And):
      return q[ JeevesLib.jor(ast[tree.left], ast[tree.right]) ]

    # thn if cond else els
    # JeevesLib.jif(cond, lambda : thn, lambda : els)
    if isinstance(tree, IfExp):
      return q[ JeevesLib.jif(ast[tree.test], lambda : ast[tree.body], lambda : ast[tree.orelse]) ]

    # a = b
    # a = JeevesLib.jassign(a, b)
    if isinstance(tree, Assign):
      # TODO handle multiple assignments case later
      # TODO handle cases where the left-hand side isn't so simple
      assert len(tree.targets) == 1
      return copy_location(
        Assign([tree.targets[0]], q[ JeevesLib.jassign(ast[tree.targets[0]], ast[tree.value]) ]),
        tree
       )

    # a += b
    # a += Reassign(b, Reassign.Add)
    """
    if isinstance(tree, AugAssign):
      if isinstance(tree.op, And):
        op = q[lambda x,y : x+y]
      elif isinstance(tree.op, Sub):
        op = q[lambda x,y : x-y]
      else:
        assert False # TODO other operators
      return copy_location(
        AugAssign(tree.targets[0], Add(), q[ JeevesLib.Reassign(ast[tree.value], ast[op]) ]),
        tree
       )
    """

    # in every function, find all variables that get assigned and initialize them
    # to Unassigned()
    if isinstance(tree, FunctionDef):
      varnames = get_vars_in_scope(tree)
      newstmt = Assign([Name(id=name,ctx=Store()) for name in varnames],
            q[JeevesLib.Unassigned()])
      name = tree.name
      args = transform.recurse(tree.args) 
      body = transform.recurse(tree.body)
      decorator_list = transform.recurse(tree.decorator_list)
      newtree = copy_location(
        FunctionDef(name=name, args=args,
                body=[newstmt]+body,
                decorator_list=decorator_list),
        tree
      )
      stop()
      return newtree

  return transform.recurse(tree)
