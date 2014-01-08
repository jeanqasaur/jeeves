'''
Questions:
- Can we get what we need by subclassing Model?
'''
from django.db import Models

# Make a Jeeves Model that enhances the vanilla Django model with information
# about how labels work and that kind of thing. We'll also need to override
# some methods so that we can create records and make queries appropriately.
class JeevesModel(models.Model):
  # Can we implement a Jeeves model on top of the regular model without
  # overloading everything?

  # Is this how we want to set up the Jeeves API?
  def get(id):
    pass
