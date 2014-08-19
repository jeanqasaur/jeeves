import coursemanager.models as coursemanager
from django.contrib.auth.models import User
from datetime import datetime

'''
UserProfiles.
'''
jeanyangUser=coursemanager.UserProfile.objects.create(
    username="jeanyang"
  , email="jeanyang@mit.edu"
  , name="Jean Yang"
  , role='a'
)

benUser=coursemanager.UserProfile.objects.create(
    username="ben"
  , email="ben@mit.edu"
  , name="Ben Shaibu"
  , role='s')
User.objects.create_user('ben', 'ben@mit.edu', 'ben')
janeUser=coursemanager.UserProfile.objects.create(
    username="jane"
  , email="janedoe@mit.edu"
  , name="Jane Doe"
  , role='s')
User.objects.create_user('jane', 'janedoe@mit.edu', 'jane')

rishabhUser=coursemanager.UserProfile.objects.create(
    username="rishabh"
  , email="risgreat@gmail.com"
  , name="Rishabh Singh"
  , role='i')
User.objects.create_user('rishabh', 'risgreat@gmail.com', 'rishabh')

phwUser=coursemanager.UserProfile.objects.create(
    username="phw"
  , email="phw@mit.edu"
  , name="Patrick Henry Winston"
  , role='i')
User.objects.create_user('phw', 'phw@mit.edu', 'phw')

rcmUser=coursemanager.UserProfile.objects.create(
    username="rcm"
  , email="rcm@mit.edu"
  , name="Rob Miller"
  , role='i')
User.objects.create_user('rcm', 'rcm@mit.edu', 'rcm')

'''
Courses.
'''
course803=coursemanager.Course.objects.create(
    name="Human Intelligence Enterprise"
  , courseId="6.803")
coursemanager.CourseInstructor.objects.create(
    course=course803
  , instructor=phwUser)
course813=coursemanager.Course.objects.create(
    name="User Interface Design"
  , courseId="6.813")
coursemanager.CourseInstructor.objects.create(
    course=course813
  , instructor=rcmUser)
coursemanager.CourseInstructor.objects.create(
    course=course813
  , instructor=rishabhUser)

'''
Students and courses.
'''
StudentCourse.objects.create(
    student=benUser
  , course=course803
  , grade='A')
StudentCourse.objects.create(
    student=benUser
  , course=course813
  , grade='B')
StudentCourse.objects.create(
    student=janeUser
  , course=course813
  , grade='A')

'''
Assignments.
'''
# TODO: Fix this naive datetime business.
assignment813_1=coursemanager.Assignment.objects.create(
    name="Assignment 1"
  , dueDate=datetime.strptime('2012-12-30 19:00', "%Y-%m-%d %H:%M")
  , maxPoints=100
  , prompt="Do this assignment."
  , owner=rishabhUser
  , course=course813
  )
assignment813_2=coursemanager.Assignment.objects.create(
    name="Assignment 2"
  , dueDate=datetime.strptime('2012-12-30 19:00', "%Y-%m-%d %H:%M")
  , maxPoints=100
  , prompt="Do this assignment too."
  , owner=rishabhUser
  , course=course813
  )

'''
Submissions.
'''
ben813_1=coursemanager.Submission.objects.create(
    assignment=assignment813_1
  , author=benUser
  , grade='A'
  )
ben813_2=coursemanager.Submission.objects.create(
    assignment=assignment813_2
  , author=benUser
  , grade='B'
  )
# And some comments.
ben813_1_comment0=coursemanager.SubmissionComment.objects.create(
    submission=ben813_1
  , author=rishabhUser
  , body="What a great assignment!"
  , commentPermissions='U'
  )
