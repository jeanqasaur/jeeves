from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from models import Assignment, Course, CourseInstructor, StudentCourse, Submission, SubmissionComment, UserProfile

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

# "Glue method". Right now you just write a method like `index` below.
# It returns a (faceted) tuple either of the form (template_name, template_ctxt)
# or ("redirect", redirect_url).
#
# SUPER HACKY, obviously. Ideally we would have a full object similar to the django
# HttpResponse that can be faceted. Such an object would need to support Jeeves,
# of course. And the concretized rendering should be moved to a library function
# (like render_to_response).
@jeeves
def add_to_context(context_dict, request, template_name, profile, concretize):
    template_name = concretize(template_name)
    context_dict['concretize'] = concretize

    context_dict['is_admin'] = profile != None and profile.level == "chair"
    context_dict['profile'] = profile

    context_dict['is_logged_in'] = (request.user and
                                    request.user.is_authenticated() and
                                    (not request.user.is_anonymous()))

'''
Wraps around a request by getting the user and defining functions like
concretize.
'''
def request_wrapper(view_fn, *args, **kwargs):
    def real_view_fn(request):
        try:
            profile = UserProfile.objects.get(username=request.user.username)

            ans = view_fn(request, profile, *args, **kwargs)
            template_name = ans[0]
            context_dict = ans[1]

            if template_name == "redirect":
                path = context_dict
                return HttpResponseRedirect(JeevesLib.concretize(profile, path))

            concretizeState = JeevesLib.jeevesState.policyenv.getNewSolverState(profile)
            def concretize(val):
                return concretizeState.concretizeExp(val, JeevesLib.jeevesState.pathenv.getEnv())
            add_to_context(context_dict, request, template_name, profile, concretize)

            return render_to_response(template_name, RequestContext(request, context_dict))

        except Exception:
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Clear concretization cache.
            JeevesLib.clear_cache()

    real_view_fn.__name__ = view_fn.__name__
    return real_view_fn

# An example of a really simple view.
# The argument `user_profile` is a User object (defined in models.py).
# Use this instead of `request.user` (which is the ordinary django User model).
# You can access request.POST and request.GET as normal.

@login_required
@request_wrapper
@jeeves
def index(request, user_profile):
  # TODO: Do some more things with the index here...

  return (   "index.html"
         , { 'name' : user_profile.name } )

'''
Looking at an assignment. Different users have different policies.
'''
@login_required
@request_wrapper
@jeeves
def assignments_view(request, user_profile):
  course_id = request.GET.get('course_id')
  course = Course.objects.get(jeeves_id=course_id)

  # TODO: Use a join to get the submissions associated with the assignment.
  assignments = Assignment.objects.filter(course=course).all()
  # TODO: Add field that links to the student submission.
  idx = 0
  for a in assignments:
    a.label = "collapse" + str(idx)
    idx += 1

  scs = StudentCourse.objects.filter(course=course).all()
  # TODO: Remove the current student.

  return ( "course_assignments.html"
          , { "assignments" : assignments
            , "scs": scs } )

@login_required
@request_wrapper
@jeeves
def courses_view(request, user_profile):
  studentcourses = JeevesLib.concretize(user_profile, StudentCourse.objects.filter(student=user_profile).all())
  print studentcourses
  courses = []
  for sc in studentcourses:
    c = sc.course
    c.grade = sc.grade
    c.instructors = CourseInstructor.objects.filter(course=c)
    print c.instructors
    courses.append(c)

  assignments = Assignment.objects.all()

  return ( "courses.html"
         , {  'name' : user_profile.name
            , 'courses' : courses
            , 'which_page' : "courses" } )

@login_required
@request_wrapper
@jeeves
def submission_view(request, user_profile):
  # TODO: Does this require there to be a submission id?
  submission_id = request.GET.get('submission_id')
  submission = Submission.objects.get(jeeves_id=submission_id)

  # Now get the comments.
  comments = SubmissionComment.objects.filter(submission=submission)

  return ( "submission.html"
          , { "submission" : submission
            , "comments" : comments
            , "comments_length" : len(comments) } )

@login_required
@request_wrapper
@jeeves
def submissions_view(request, user_profile):
  # Get submissions associated with the current user.
  user_submissions = Submission.objects.filter(author=user_profile).all()

  return ( "submissions.html"
         , { "submissions" : user_submissions
           , "which_page" : "submissions" } )

@login_required
@request_wrapper
@jeeves
def profile_view(request, user_profile):
    if request.method == 'GET':
      username = request.GET.get('username', '')
      if (username != ''):
        profile = UserProfile.objects.get(username=username)
      else:
        profile = user_profile
    else:
      profile = user_profile
 
    if request.method == 'POST':
      assert (username == user_profile.username)
      user_profile.email = request.POST.get('email', '')
      user_profile.name = request.POST.get('name', '')
      user_profile.role = request.POST.get('role', '')
      user_profile.save()

    return ("profile.html", {
        "user_profile": profile
      , "name": profile.name
      , "which_page": "profile"
    })

def register_account(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("index")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()

            User.objects.create(
                username=user.username
              , email=request.POST.get('email', '')
              , name=request.POST.get('name', '')
              , role=request.POST.get('role', '')
            )

            user = authenticate(username=request.POST['username'],
                         password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()

    return render_to_response("registration/account.html", RequestContext(request,
        {
            'form' : form,
            'which_page' : "register"
        }))
