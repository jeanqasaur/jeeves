import datetime

from django import template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from jinja2 import filters
import pytz

from models import Event, EventHost, EventGuest, UserProfile

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

def get_type(form_field_obj):
    return form_field_obj.widget.__class__.__name__

filters.FILTERS['get_type'] = get_type

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

            concretizeState = \
                JeevesLib.jeevesState.policyenv.getNewSolverState(profile)
            def concretize(val):
                return concretizeState.concretizeExp(
                    val, JeevesLib.jeevesState.pathenv.getEnv())
            add_to_context(context_dict
                , request, template_name, profile, concretize)

            return render_to_response(
                template_name
                , RequestContext(request, context_dict))


        except Exception:
            import traceback
            traceback.print_exc()
            raise

    real_view_fn.__name__ = view_fn.__name__
    return real_view_fn

@login_required
@request_wrapper
@jeeves
def index(request, user_profile):
    # TODO: Load calendar items.
    user_events = user_profile.get_events()

    return (   "index.html"
           , {'name' : user_profile.name
             , 'events' : user_events} )

@login_required
@request_wrapper
def event(request, user_profile):
    event_id = request.GET.get('id', '')
    fields = {}
    
    # If we're adding an event.
    if request.method == 'POST':
        name = request.POST.get('name', 'Unnamed event')
        location = request.POST.get('location', 'Undisclosed location')
        time = request.POST.get('time', datetime.datetime.now(tz=pytz.utc))
        description = request.POST.get('description',  '')
        visibility = request.POST.get('visibility', 'E')
        fields = {'name': name, 'location': location, 'time': time
            , 'description': description, 'visibility': visibility}

        # If the event already exists.
        if event_id != '':
            event = Event.objects.get(jeeves_id=event_id)
            event.name = name
            event.location = location
            event.time = time
            event.description = description
            event.visibility = visibility
            event.save()
        else:
            event = Event.objects.create(name=name
            , location=location
            , time=time
            , description=description
            , visibility=visibility)
            return ("redirect", "event?id=" + event.jeeves_id)
    else:
        if (event_id != ''):
            event = Event.objects.get(jeeves_id=event_id)
            fields = {'name': event.name, 'location': event.location
                , 'time': event.time, 'description': event.description
                , 'visibility': event.visibility}

    # If we're just showing the form.
    return ("event.html", fields)

@login_required
@request_wrapper
@jeeves
def profile_view(request, user_profile):
    profile = UserProfile.objects.get(username=request.user.username)
    if profile == None:
        profile = user_profile
    
    if request.method == 'POST':
        assert(request.user.username==userprofile.username)
        profile.name = request.POST.get('name', '')
        profile.email = request.POST.get('email', '')
        profile.save()

    host_events = EventHost.objects.filter(host=profile).all()
    guest_events = EventGuest.objects.filter(guest=profile).all()

    return ("profile.html", {
        "profile": profile,
        "is_own_profile": request.user.username==user_profile.username,
        "host_events": host_events,
        "guest_events": guest_events,
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

            UserProfile.objects.create(
                username=user.username,
                email=request.POST.get('email', ''),
            )

            user = authenticate(username=request.POST['username'],
                         password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()

    return render_to_response("registration/account.html"
        , RequestContext(request,
        {'form': form,
        'which_page' : "register"}))
