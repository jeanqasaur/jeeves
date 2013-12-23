from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

import common

"""
Adds the @JeevesLib.supports_jeeves decorator to indicate that the function
supports Jeeves
"""

def add_supports_jeeves(node):
  @Walker
  def transform(tree, stop, **kw):
    if isinstance(tree, FunctionDef) or isinstance(tree, ClassDef):
      tree.decorator_list.insert(0, q[JeevesLib.supports_jeeves])

    if isinstance(tree, Lambda):
      args = tree.args
      body = transform.recurse(tree.body)
      stop()
      return q[JeevesLib.supports_jeeves(ast[Lambda(args, body)])]

  return transform.recurse(node)
