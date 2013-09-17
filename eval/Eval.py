'''
NOTE(JY): In Transformer.scala, we essentially do a bunch of weird stuff to
get the equivalent of type classes for overloading. I don't think we have to do
that in Python.
'''
class Eval:
  '''
  This function should combine two 

  NOTE(JY): We should just be able to use the universal Facet constructor
  instead of the weird stuff we were doing before... You may need to change
  things to get it to work though!
  '''
  def facetJoin(f0, f1, opr):
    # In here you will need to determine if something is a facet or not a
    # facet. Typecase?
    return NotImplemented
