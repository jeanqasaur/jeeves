from django.conf import settings
from django.db.models import CharField, DateTimeField, FileField, IntegerField, TextField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
import os
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

ROLE = (
    ('s', 'Student')
  , ('i', 'Instructor')
  , ('a', 'Admin')
  )

GRADE = (
    ('A', 'A')
  , ('B', 'B')
  , ('C', 'C')
  , ('D', 'D')
  , ('F', 'F')
)

class UserProfile(Model):
  username = CharField(max_length=1024)
  email = CharField(max_length=1024)
  name = CharField(max_length=256)
  role = CharField(max_length=1) #, choices=ROLE)

class Course(Model):
  name = CharField(max_length=1024)
  courseId = CharField(max_length=1024)

# Maps courses to instructors.
class CourseInstructor(Model):
  course = ForeignKey(Course, null=True, related_name='courseinstructor_course')
  instructor = ForeignKey(UserProfile, null=True, related_name='courseinstructor_instructor')

class StudentCourse(Model):
  student = ForeignKey(UserProfile, null=True, related_name='studentcourse_student')
  course = ForeignKey(Course, null=True, related_name='studentcourse_course')
  grade = CharField(max_length=1) #, choices=GRADE)

class Assignment(Model):
  name = CharField(max_length=1024)
  dueDate = DateTimeField()
  maxPoints = IntegerField()
  prompt = TextField()
  owner = ForeignKey(UserProfile, null=True, related_name='assignment_user')
  course = ForeignKey(Course, null=True, related_name='assignment_course')

  # TODO: Policies

class Submission(Model):
  title = CharField(max_length=1024)
  assignment = ForeignKey(Assignment, null=True)
  author = ForeignKey(UserProfile, null=True)
  uploadFile = FileField(upload_to='submissions')
  submitDate = DateTimeField(auto_now=True)
  grade = CharField(max_length=1, choices=GRADE)

class StudentSubmission(Model):
  user = ForeignKey(UserProfile, null=True, related_name='studentsubmission_student')
  submission = ForeignKey(Submission, null=True, related_name='studentsubmission_submission')

class Comment(Model):
  author = ForeignKey(UserProfile, null=True)
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
