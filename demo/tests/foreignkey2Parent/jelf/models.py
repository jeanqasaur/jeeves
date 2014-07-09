from django.db.models import CharField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
from sourcetrans.macro_module import macros, jeeves
from jeevesdb.JeevesModel import label_for

import JeevesLib

# An example model.
# Right now self-reference is either impossible or difficult because JeevesForeignKey
# only supports a model class (not a string) as the related object. (TODO fix this.)
class UserProfile(Model):
    username = CharField(max_length=1024)
    email = CharField(max_length=1024)

class Address(Model):
	zipcode=CharField(max_length=5)
	def String(self):
		return self.zipcode

class Individual(Model):
	address = ForeignKey(Address, blank=True, null = True)
	def Address(self):
		return self.address
	@staticmethod
	def jeeves_get_private_address(individual):
		restrictedAddress=Address.objects.create(zipcode=individual.address.zipcode[:2]+"***")
		return restrictedAddress
	@staticmethod
	@label_for('address')
	@jeeves
	def jeeves_restrict_Individuallabel(individual, ctxt):
		return False

from django.dispatch import receiver
from django.db.models.signals import post_syncdb
import sys
current_module = sys.modules[__name__]

@receiver(post_syncdb, sender=current_module)
def dbSynced(sender, **kwargs):
	execfile("sampleData.py")
