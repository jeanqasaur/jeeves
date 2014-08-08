import coursemanager.models as coursemanager
from datetime import datetime

rishabhUser=coursemanager.Instructor.objects.create(
    username="rishabh"
  , email="risgreat@gmail.com"
  , firstName="Rishabh"
  , lastName="Singh")

# TODO: Fix this naive datetime business.
rishabhAssignment=coursemanager.Assignment.objects.create(
    name="Assignment 1"
  , dueDate=datetime.strptime('2012-12-30 19:00', "%Y-%m-%d %H:%M")
  , maxPoints=100
  , prompt="Do this assignment."
  , owner=rishabhUser
  )
