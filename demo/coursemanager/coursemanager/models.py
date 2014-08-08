from django.conf import settings
from django.db.models import CharField, DateTimeField, FileField, IntegerField, TextField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
import os
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

class User(Model):
  username = CharField(max_length=1024)
  email = CharField(max_length=1024)
  firstName = CharField(max_length=256)
  lastName = CharField(max_length=256)

# TODO: Does subclassing tables work? It should...
class Student(User):
  pass

class Instructor(User):
  pass

class Assignment(Model):
  name = CharField(max_length=1024)
  dueDate = DateTimeField()
  maxPoints = IntegerField()
  prompt = TextField()
  owner = ForeignKey(Instructor, null=True, related_name='assignment_user')

  # TODO: Policies

class Submission(Model):
  title = CharField(max_length=1024)
  assignment = ForeignKey(Assignment, null=True)
  author = ForeignKey(User, null=True)
  uploadFile = FileField(upload_to='submissions')
  submitDate = DateTimeField(auto_now=True)
  grade = CharField(max_length=48)

class UserSubmission(Model):
  user = ForeignKey(User, null=True, related_name='usersubmission_user')
  submission = ForeignKey(Submission, null=True, related_name='usersubmission_submission')

class Comment(Model):
  author = ForeignKey(User, null=True)
  submitDate = DateTimeField(auto_now=True)
  body = TextField()

from django.dispatch import receiver
from django.db.models.signals import post_syncdb
import sys
current_module = sys.modules[__name__]
@receiver(post_syncdb, sender=current_module)
def dbSynced(sender, **kwargs):
  if settings.DEBUG:
    execfile(os.path.join(settings.BASE_DIR, '..', 'sampleData.py'))
