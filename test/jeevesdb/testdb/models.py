from django.db import models
from jeevesdb import JeevesModel

class Animal(models.Model):
  # TODO: Allow this to be a JeevesModel.JeevesModel. Right now this doesn't
  # validate...
  name = models.CharField(max_length=30)
  sound = models.CharField(max_length=30)

  def speak(self):
    return "The %s says \"%s\"" % (self.name, self.sound)
