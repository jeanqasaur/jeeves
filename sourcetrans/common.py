from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

@Walker
def toParam(tree, **kw):
  if isinstance(tree, Store):
    return Param()

@Walker
def toLoad(tree, **kw):
  if isinstance(tree, Store):
    return Load()

def storeToParam(node):
  return toParam.recurse(node)

def storeToLoad(node):
  return toLoad.recurse(node)
