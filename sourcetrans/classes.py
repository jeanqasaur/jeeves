from macropy.core.macros import *
from macropy.core.quotes import macros, q, ast, u
from ast import *

def classes_transform(node, gen_sym):
  @Walker
  def transform(tree, **k2):
    if isinstance(tree, ClassDef):
      # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

      # Add the function
      # def __setattr__(self, attr, value):
      #   self.__dict__[attr] = jassign(self.__dict__.get(attr, Unassigned()), value)
      self_name = gen_sym()
      attr_name = gen_sym()
      value_name = gen_sym()
      newfunc = FunctionDef(
        name="__setattr__",
        args=arguments(
          args=[Name(id=self_name,ctx=Param()),
                Name(id=attr_name,ctx=Param()),
                Name(id=value_name,ctx=Param()),
               ],
          vararg=None,
          kwarg=None,
          defaults=[]
        ),
        decorator_list=[],
        body=[
          Assign([Subscript(
            value=Attribute(
              value=Name(id=self_name, ctx=Load()),
              attr="__dict__",
              ctx=Load(),
            ),
            slice=Index(Name(id=attr_name, ctx=Load())),
            ctx=Store(),
          )],
          q[ JeevesLib.jassign(name[self_name].__dict__.get(name[attr_name],
                JeevesLib.Unassigned()), name[value_name]) ]
          )
        ]
      )

      return copy_location(ClassDef(
        name=tree.name,
        bases=tree.bases,
        body=[newfunc] + tree.body,
        decorator_list=tree.decorator_list,
      ), tree)

  return transform.recurse(node)
