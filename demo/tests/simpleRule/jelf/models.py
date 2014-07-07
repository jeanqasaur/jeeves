from django.db.models import CharField
from jeevesdb.JeevesModel import JeevesModel, JeevesForeignKey
from sourcetrans.macro_module import macros, jeeves
from jeevesdb.JeevesModel import label_for

import JeevesLib

# An example model.
# Right now self-reference is either impossible or difficult because JeevesForeignKey
# only supports a model class (not a string) as the related object. (TODO fix this.)
class UserProfile(JeevesModel):
    username = CharField(max_length=1024)
    email = CharField(max_length=1024)

class individual(JeevesModel):
	ssn = CharField(max_length=9)
	
	@staticmethod
	def jeeves_get_private_ssn(user):
		return ""
	
	@staticmethod
	@label_for('ssn')
	@jeeves
	def jeeves_restrict_individuallabel(address, ctxt):
		return False

from django.dispatch import receiver
from django.db.models.signals import post_syncdb
import sys
current_module = sys.modules[__name__]

@receiver(post_syncdb, sender=current_module)
def dbSynced(sender, **kwargs):
	execfile("sampleData.py")
