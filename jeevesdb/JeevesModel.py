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
  # overloading everything? (Let's try!)
  def __init__(self):
    # Make sure superclass constructor gets called first and then pass all
    # of the Django manager attributes to the Jeeves API. The Jeeves API can
    # then manipulate it.
    self.jeeves = JeevesAPI(self.objects, self.filter, self.all)

  # One extra column with one label for now.
  # Eventually, we'll need a list of labels to capture things we save. At that
  # point, we'll also need to figure out a strategy for not making labels
  # blow up.
