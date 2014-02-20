from django.db import models
from jeevesdb import JeevesModel

class Animal(JeevesModel.JeevesModel):
  name = models.CharField(max_length=30)
  sound = models.CharField(max_length=30)

  def speak(self):
    return "The %s says \"%s\"" % (self.name, self.sound)

class Zoo(JeevesModel.JeevesModel):
  name = models.CharField(max_length=30)
  inhabitant = JeevesModel.JeevesForeignKey(Animal)
