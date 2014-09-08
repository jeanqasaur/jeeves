from django.conf import settings
from django.db.models import CharField, DateTimeField, FileField, IntegerField, TextField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for

import os
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

ROLE = (('s', 'Student')
	, ('i', 'Instructor')
	, ('a', 'Admin'))

GRADE = (('A', 'A')
	, ('B', 'B')
	, ('C', 'C')
	, ('D', 'D')
	, ('F', 'F')
	, ('U', 'Unknown'))

class UserProfile(Model):
	username = CharField(max_length=1024)
	email = CharField(max_length=1024)
	name = CharField(max_length=1024)
	role = CharField(max_length=1, choices=ROLE)

	@staticmethod
	def jeeves_get_private_email(user):
		return "[redacted]"

	@staticmethod
	@label_for('email')
	@jeeves
	def jeeves_restrict_userprofilelabel(user, ctxt):
		return user == ctxt

	@jeeves
	def is_instructor(self, course):
		return CourseInstructor.objects.get(course=course, instructor=self) \
			!= None

	class Meta:
		db_table='coursemanager_userprofile'

class Course(Model):
	name = CharField(max_length=1024)
	courseId = CharField(max_length=1024)

# Maps courses to instructors.
class CourseInstructor(Model):
	course = ForeignKey(Course, null=True
		, related_name='courseinstructor_course')
	instructor = ForeignKey(UserProfile, null=True
		, related_name='courseinstructor_instructor')

class StudentCourse(Model):
	student = ForeignKey(UserProfile, null=True, related_name='students')
	course = ForeignKey(Course, null=True, related_name='studentcourse_course')
	grade = CharField(max_length=1, choices=GRADE)

	@staticmethod
	def jeeves_get_private_grade(sc):
		return 'U'
	
	@staticmethod
	@label_for('grade')
	@jeeves
	def jeeves_restrict_grade(sc, ctxt):
		"""Only the student can see the grade.
		"""
		return sc.student == ctxt or ctxt.is_instructor(sc.course)

	class Meta:
		db_table='coursemanager_studentcourse'

class Assignment(Model):
	name = CharField(max_length=1024)
	dueDate = DateTimeField()
	maxPoints = IntegerField()
	prompt = TextField()
	owner = ForeignKey(UserProfile, null=True, related_name='assignment_user')
	course = ForeignKey(Course, null=True, related_name='assignment_course')

	@jeeves
	def get_average(self):
		submissions = Submission.objects.filter(assignment=self).all()
		sum_scores = 0.0
		total = 0
		for s in submissions:
			sum_scores += s.score
			total += 1
		return 0.0 if total == 0 else float(sum_scores/total)

class Submission(Model):
	assignment = ForeignKey(Assignment, null=True
		, related_name='submission_assignment')
	author = ForeignKey(UserProfile, null=True
		, related_name='submission_author')
	uploadFile = FileField(upload_to='submissions')
	submitDate = DateTimeField(auto_now=True)
	grade = CharField(max_length=1, choices=GRADE)
	score = IntegerField()

	@staticmethod
	def jeeves_get_private_uploadFile(s):
		return None
	
	@staticmethod
	def jeeves_get_private_grade(s):
		return 'U'

	@staticmethod
	@label_for('uploadFile', 'grade')
	@jeeves
	def jeeves_restrict_uploadFile(s, ctxt):
		return s.author == ctxt or ctxt.is_instructor(s.assignment.course)

COMMENT_PERMISSION = (('U', "Only visible to user")
	, ('I', "Only visible to instructors")
	, ('E', "Visible to everyone"))
class SubmissionComment(Model):
	submission = ForeignKey(Submission, null=True
		, related_name='submissioncomment_submission')
	author = ForeignKey(UserProfile, null=True)
	submitDate = DateTimeField(auto_now=True)
	body = TextField()
	commentPermissions = CharField(max_length=1, choices=COMMENT_PERMISSION)

from django.dispatch import receiver
from django.db.models.signals import post_syncdb
import sys
current_module = sys.modules[__name__]
@receiver(post_syncdb, sender=current_module)
def dbSynced(sender, **kwargs):
	if settings.DEBUG:
		execfile(os.path.join(settings.BASE_DIR, '..', 'SampleData.py'))
