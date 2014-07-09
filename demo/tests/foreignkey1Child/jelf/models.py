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
	@staticmethod
	def jeeves_get_private_zipcode(address):
		print locals()
		print "Address",address
		return address.zipcode[:2]+"***"
	@staticmethod
	@label_for('zipcode')
	@jeeves
	def jeeves_restrict_Addresslabel(address, ctxt):
		return False

class Individual(Model):
	address = ForeignKey(Address, blank=True, null = True)
	def Address(self):
		return self.address

from django.dispatch import receiver
from django.db.models.signals import post_syncdb
import sys
current_module = sys.modules[__name__]

@receiver(post_syncdb, sender=current_module)
def dbSynced(sender, **kwargs):
	execfile("sampleData.py")
