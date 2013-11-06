from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

import common

import copy

"""
Replace if-statments and for-blocks with jif and jmap
"""
def body_stmts_transform(tree, gen_sym):
  @Walker
  def transform(tree, stop, **kw):
    # If a1,a2,..,an are all the local variables, change
    #
    # if condition:
    #     thn_body
    # else:
    #     els_body
    # 
    # to
    #
    # def thn_fn_name():
    #     thn_body
    # def els_fn_name():
    #     els_body
    # jif(condition, thn_fn_name, els_fn_name)
    if isinstance(tree, If):
      # TODO search over the bodies, and only do this for the variables that
      # get assigned to.
      thn_fn_name = gen_sym()
      els_fn_name = gen_sym()

      test = transform.recurse(tree.test)
      thn_body = transform.recurse(tree.body)
      els_body = transform.recurse(tree.orelse)
      stop()

      def get_func(funcname, funcbody):
        return FunctionDef(
          name=funcname, 
          args=arguments(
            args=[],
            vararg=None,
            kwarg=None,
            defaults=[],
          ),
          body=funcbody or [Pass()],
          decorator_list=[],
        )

      return [
        get_func(thn_fn_name, thn_body),
        get_func(els_fn_name, els_body),
        Expr(value=q[
          JeevesLib.jif(ast[test],
            ast[Name(id=thn_fn_name,ctx=Load())],
            ast[Name(id=els_fn_name,ctx=Load())],
          )
        ])
      ]

    if isinstance(tree, For):
      body_fn_name = gen_sym()

      iter = transform.recurse(tree.iter)
      body = transform.recurse(tree.body)
      targetParams = common.storeToParam(copy.deepcopy(tree.target))
      assert len(tree.orelse) == 0 or isinstance(tree.orelse[0], Pass)
      stop()

      func = copy_location(FunctionDef(
        name=body_fn_name,
        args=arguments(
          args=[targetParams],
          vararg=None,
          kwarg=None,
          defaults=[],
        ),
        body=body,
        decorator_list=[]
      ), tree)

      return [
        func,
        Expr(value=q[ JeevesLib.jmap(ast[iter], ast[Name(body_fn_name,Load())]) ])
      ]

  return transform.recurse(tree)
