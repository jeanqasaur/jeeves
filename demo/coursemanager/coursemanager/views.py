from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from models import Assignment, Course, CourseInstructor, StudentCourse, StudentSubmission, UserProfile

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
  return (   "index.html"
         , { 'name' : user_profile.name } )

@login_required
@request_wrapper
def courses_view(request, user_profile):
  # TODO: Figure out this business about filtering on FObjects.
  randomuser = UserProfile.objects.all()[0]
  print user_profile.v
  print randomuser

  studentcourses = StudentCourse.objects.filter(student=user_profile.v)
  courses = []
  for sc in studentcourses:
    print sc
    c = sc.course
    c.grade = sc.grade
    c.instructors = []
    courseInstructors = list(CourseInstructor.objects.filter(course=c.v))
    for ci in courseInstructors:
      c.instructors.append(ci.instructor)
    courses.append(c)

  return ( "courses.html"
         , {  'name' : user_profile.name
            , 'courses' : courses
            , 'which_page' : "courses" } )

@login_required
@request_wrapper
def submissions_view(request, user_profile):
  return ( "submissions.html"
         , { "which_page": "submissions" } )

@login_required
@request_wrapper
@jeeves
def profile_view(request, user_profile):
    profile = UserProfile.objects.get(username=request.user.username)
    if profile == None:
        profile = UserProfile(username=request.user.username)
    
    if request.method == 'POST':
#        profile.email = request.POST.get('email', '')
        profile.save()

    return ("profile.html", {
#        "email": profile.email,
        "which_page": "profile",
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
