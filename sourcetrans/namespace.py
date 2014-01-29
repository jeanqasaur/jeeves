from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

import common
import copy

# Returns a list of the vars assigned to in an arguments node
def get_params_in_arguments(node):
  @Walker
  def get_params(tree, collect, **kw):
    if isinstance(tree, Name):
      collect(tree.id)
  _, p1 = get_params.recurse_collect(node.args)
  _, p2 = get_params.recurse_collect(node.vararg)
  _, p3 = get_params.recurse_collect(node.kwarg)
  return p1 + p2 + p3

# Takes a FunctionDef node and returns a pair
# (list of local variables, list of parameter variables)
def get_vars_in_scope(node):
  @Walker
  def get_vars(tree, collect, stop, **kw):
    if isinstance(tree, Name) and isinstance(tree.ctx, Store):
      collect(tree.id)
    if isinstance(tree, ClassDef):
      stop()
    if tree != node and isinstance(tree, FunctionDef):
      collect(tree.name)
      stop()
    if isinstance(tree, arguments):
      pass

  @Walker
  def get_globals(tree, collect, stop, **kw):
    if isinstance(tree, Global):
      for name in tree.names:
        collect(name)
    if tree != node and (isinstance(tree, ClassDef) or isinstance(tree, FunctionDef)):
      stop()

  _, v = get_vars.recurse_collect(node)
  _, g = get_globals.recurse_collect(node)
  p = get_params_in_arguments(node.args)
  return (list(set(v) - set(g)), p)

def replace_local_scopes_with_namespace(node, gen_sym):
  @Walker
  def transform(tree, stop, ctx, set_ctx, **kw):
    if isinstance(tree, FunctionDef):
      varNames, paramNames = get_vars_in_scope(tree)
      namespaceName = gen_sym()

      # namespaceName = Namespace({param1:value1,...},funcname)
      namespaceStmt = Assign(
        targets=[Name(id=namespaceName,ctx=Store())],
        value=Call(
          func=q[JeevesLib.Namespace],
          args=[Dict(
            keys=[Str(p) for p in paramNames],
            values=[Name(id=p, ctx=Load()) for p in paramNames],
          ),
            Str(s=tree.name)
          ],
          keywords=[],
          starargs=None,
          kwargs=None,
        )
      )

      # make a copy of the scope mapping nad update it
      scopeMapping = dict(ctx)
      for name in varNames + paramNames:
        scopeMapping[name] = namespaceName

      name = tree.name
      args = transform.recurse(tree.args, ctx=ctx) 
      body = transform.recurse(tree.body, ctx=scopeMapping)
      decorator_list = transform.recurse(tree.decorator_list, ctx=ctx)
      newtree = copy_location(
        FunctionDef(name=name, args=args,
                body=[namespaceStmt]+body,
                decorator_list=decorator_list),
        tree
      )

      stop()
      
      if tree.name in ctx and ctx[tree.name] != None:
        outerAssignStmt = copy_location(Assign(
          targets=[Attribute(
            value=Name(id=ctx[tree.name], ctx=Load()),
            attr=tree.name,
            ctx=Store()
          )],
          value=Name(id=tree.name, ctx=Load()),
        ), tree)
        return [newtree, outerAssignStmt]
      else:
        return newtree

    if isinstance(tree, Lambda):
      paramNames = get_params_in_arguments(tree.args)

      # make a copy of the scope mapping and update it
      scopeMapping = dict(ctx)
      for name in paramNames:
        scopeMapping[name] = None

      args = transform.recurse(tree.args, ctx=ctx)
      body = transform.recurse(tree.body, ctx=scopeMapping)
      newlambda = copy_location(Lambda(args=args, body=body), tree)
      stop()
      return newlambda

    if isinstance(tree, Name) and (isinstance(tree.ctx, Load) or isinstance(tree.ctx, Store) or isinstance(tree.ctx, Del)):
      if tree.id in ctx and ctx[tree.id] != None:
        return Attribute(
          value=Name(id=ctx[tree.id], ctx=Load()),
          attr=tree.id,
          ctx=tree.ctx
        )

    if isinstance(tree, For):
      # For(expr target, expr iter, stmt* body, stmt* orelse)
      target = tree.target
      iter = tree.iter
      body = tree.body
      orelse = tree.orelse
      
      stop()

      assignTarget = transform.recurse(copy.deepcopy(target), ctx=ctx)
      assignValue = common.storeToLoad(copy.deepcopy(target))
      assignStmt = Assign([assignTarget], assignValue)

      iter = transform.recurse(iter, ctx=ctx)
      body = transform.recurse(body, ctx=ctx)
      orelse = transform.recurse(orelse, ctx=ctx)

      return copy_location(
        For(target=target, iter=iter, body=[assignStmt]+body, orelse=orelse),
        tree
      )

    if isinstance(tree, arguments):
      stop()
      return arguments(
        args=tree.args,
        vararg=tree.vararg,
        kwarg=tree.kwarg,
        defaults=transform.recurse(tree.defaults, ctx=ctx)
      )

  return transform.recurse(node, ctx={})
