from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

import common

"""
move all return statements to the end of a function
"""

def return_transform(node, gen_sym):
  @Walker
  def transform(tree, **kw):
    if isinstance(tree, FunctionDef):
      hasnt_returned_var = gen_sym()
      return_value_var = gen_sym()

      def return_recurse(body):
        tail = []
        for stmt in body[::-1]:
          if isinstance(stmt, Return):
            tail = [Assign(targets=[Name(id=hasnt_returned_var,ctx=Store())],value=Name("False",Load()))]
            if stmt.value:
              tail.append(copy_location(
                Assign(targets=[Name(id=return_value_var,ctx=Store())],value=stmt.value),
                stmt
              ))
          elif isinstance(stmt, If):
            tail = [
              If(test=Name(id=hasnt_returned_var,ctx=Load()),
                body=tail[::-1],
                orelse=[Pass()],
              ),
              copy_location(
                If(test=stmt.test,
                  body=return_recurse(stmt.body),
                  orelse=return_recurse(stmt.orelse)
                ), stmt),
            ]
          elif isinstance(stmt, For):
            tail = [
              If(test=Name(id=hasnt_returned_var,ctx=Load()),
                body=tail[::-1],
                orelse=[Pass()],
              ),
              copy_location(
                For(target=stmt.target,
                  iter=stmt.iter,
                  body=[If(
                    test=Name(hasnt_returned_var,Load()),
                    body=return_recurse(stmt.body),
                    orelse=[Pass()],
                  )],
                  orelse=[Pass()]
                ), stmt),
            ]
          else:
            tail.append(stmt)

        return tail[::-1]

      tree.body = (
       [
          Assign(targets=[Name(hasnt_returned_var,Store())], value=Name("True",Load())),
          Assign(targets=[Name(return_value_var,Store())], value=Name("None",Load())),
       ] +
       return_recurse(tree.body) +
       [
          Return(value=Name(return_value_var,Load())),
       ]
      )

  return transform.recurse(node)
