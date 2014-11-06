from django.db import models
from jeevesdb import JeevesModel

class Animal(JeevesModel.JeevesModel):
  name = models.CharField(max_length=30)
  sound = models.CharField(max_length=30)

  @staticmethod
  def jeeves_get_private_sound(animal):
    return ""

  @staticmethod
  @JeevesModel.label_for('sound')
  def jeeves_restrict_awplabel(animal, ctxt):
    return ctxt == animal

class Zoo(JeevesModel.JeevesModel):
  name = models.CharField(max_length=30)
  inhabitant = JeevesModel.JeevesForeignKey(Animal)

'''
class AnimalWithPolicy(JeevesModel.JeevesModel):
  name = models.CharField(max_length=30)
  sound = models.CharField(max_length=30)

  @staticmethod
  def jeeves_get_private_sound(animal):
    return ""

  @staticmethod
  def jeeves_restrict_sound(animal, ctxt):
    return ctxt == animal
'''
