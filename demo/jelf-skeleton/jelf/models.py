from django.db.models import Model, CharField
from jeevesdb.JeevesModel import JeevesModel, JeevesForeignKey
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

# An example model.
# Right now self-reference is either impossible or difficult because JeevesForeignKey
# only supports a model class (not a string) as the related object. (TODO fix this.)
class UserProfile(JeevesModel):
    username = CharField(max_length=1024)
    email = CharField(max_length=1024)
