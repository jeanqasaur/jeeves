from django.db.models import CharField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

# An example model.
# Right now self-reference is either impossible or difficult because JeevesForeignKey
# only supports a model class (not a string) as the related object. (TODO fix this.)
class UserProfile(Model):
	username = CharField(max_length=1024)
	email = CharField(max_length=1024)

	@staticmethod
	def jeeves_get_private_email(user):
		return "[redacted]"

	@staticmethod
	@label_for('email')
	@jeeves
	def jeeves_restrict_userprofilelabel(user, ctxt):
		return user == ctxt
