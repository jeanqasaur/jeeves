"""Views for HIPAA case study.

    :synopsis: Code for displaying HIPAA demo pages.

.. moduleauthor:: Ariel Jacobs <arielj@mit.edu>
.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect #, HttpResponse
#from django.contrib.auth.models import User
#from django.views import generic
from datetime import date
#import urllib
#import random

from jelf.models import Diagnosis, Individual, CoveredEntity, UserProfile, Transaction, Treatment

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

# TODO: Figure out what this is used for and write a comment about it.
INFORMATION_SET = {
      "preview" : "5 regarding Joe McGray"
    , "treatments" : [
          {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
         , "Service" : "ADA:D4211"
         , "DatePerformed" : date(2012, 6, 26)
		     , "PrescribingEntity" : {"Name" : "Cooper Base Dental", "ID" : 5}
         , "PerformingEntity" : {"Name" : "Cooper Base Dental", "ID" : 5}}
        , {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
         , "Service" : "D7287"
			   , "DatePerformed" : date(2013, 1, 3)
         , "PrescribingEntity" : {"Name" : "Beautiful Smile", "ID" : 23}
         , "PerformingEntity" : {"Name" : "Mary Orman, DDS", "ID" : 942}}]
    , "diagnoses" : [
          {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
         , "Manifestation" : "B01.0"
         , "DateRecognized" : date(2013, 2, 1)
         , "RecognizingEntity" : {"Name" : "Solomon Health", "ID" : 7}
         , "Diagnosis" : "Negative"}
        , {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
          , "Manifestation" : "T84.012"
          , "DateRecognized" : date(2013, 10, 17)
          , "RecognizingEntity" : {"Name" : "Dr. Wragley Medical Center"
                                 , "ID" : 130}
          , "Diagnosis" : "Positive"}]
    , "hospitalVisits" : [
        {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
       , "DateAdmitted" : date(2014, 5, 25)
       , "Location" : "113B"
       , "Condition" : "Recovering"
       , "ReligiousAffiliation" : "None"}]}

def register_account(request):
    """Account registration.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect("index")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = request.POST.get('email', '')
            user.save()

            profiletype = request.POST.get('profiletype', '')
            individual = None
            entity = None
            associate = None
            UserProfile.objects.create(
                  user=user
                , name=request.POST.get('name', '')
                ,	email=request.POST.get('email', '')
                , individual=individual
                , entity=entity
                , associate=associate
                , profiletype=int(profiletype)
			      )
            user = authenticate(username=request.POST['username'],
            password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()

    return render_to_response("registration/account.html"
        , RequestContext(request,
		        {'form' : form
           , 'which_page' : "register"}))

@jeeves
def add_to_context(context_dict, request, template_name, profile, concretize):
    """Adds relevant arguments to the context.
    """
    template_name = concretize(template_name)
    context_dict['concretize'] = concretize
    context_dict['profile'] = profile
    context_dict['is_logged_in'] = (request.user and
                                    request.user.is_authenticated() and
                                    (not request.user.is_anonymous()))

def request_wrapper(view_fn):
    """Wraps requests by setting the current viewing context and fetching the
    profile associated with that context.
    """
    def real_view_fn(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
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
            add_to_context(
                context_dict, request, template_name, profile, concretize)
            return render_to_response(
                template_name, RequestContext(request, context_dict))
        except Exception:
            import traceback
            traceback.print_exc()
            raise
    real_view_fn.__name__ = view_fn.__name__
    return real_view_fn

@login_required
@request_wrapper
@jeeves
def index(request, profile):
    """The main page shows patients and entities.
    """
    patients = Individual.objects.all()
    entities = CoveredEntity.objects.all()
    
    # TODO: Filter out ones you can't see?

    data = {"patients": patients
          , "entities": entities
          , 'name': profile.name}
    return ("index.html", data)

@request_wrapper
@jeeves
def about_view(request, user):
    """About the system.
    """
    # TODO: This doesn't work.
    return ("about.html"
            , {'which_page' : "about"})

@login_required
@request_wrapper
@jeeves
def profile_view(request, profile):
    """Displaying and updating profiles.
    """
    class FormField(object):
        """Field of a profile form.
        """
        def __init__(self, name, privacy, label, inputtype, val, disabled=True):
            self.name = name
            self.privacy = privacy
            self.label = label
            self.inputtype = inputtype
            self.val = val
            self.disabled = disabled
            self.required = self.disabled

    if profile == None:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        '''
        profile.user.first_name = request.POST.get('firstname', '')
        profile.user.last_name = request.POST.get('lastname', '')
        profile.user.email = request.POST.get('email', '')
        profile.user.save()

        profile.profiletype = int(request.POST.get('profiletype', '1'))
        '''
        profile.save()

    fields = [FormField("email", "Visible only to you", "Email", "email"
               , profile.user.email)
             , FormField("name", "Visible to everyone", "Name"
                , "text", profile.name)
             , FormField("profiletype", "Visible to everyone", "Type", "text"
                , profile.profiletype)]

    return ("profile.html", {
        "fields": fields
        , "which_page": "profile"})

@login_required
@request_wrapper
@jeeves
def users_view(request, profile):
    """Viewing all users.
    """
    # TODO: Have a better mechanism than this for letting someone know they
    # can't see something.
    if profile.type != 3:
        return ("redirect", "/index")

    user_profiles = UserProfile.objects.all()

    if request.method == 'POST':
        for profile in user_profiles:
            query_param_name = 'level-' + profile.username
            level = request.POST.get(query_param_name, '')
            if level in ['normal', 'pc', 'chair']:
                profile.level = level
                profile.save()

    return ("users_view.html", {
        'user_profiles': user_profiles,
        'which_page' : "users"
    })

@login_required
@request_wrapper
@jeeves
def treatments_view(request, profile, patient):
    """Treatments.
    """
    p = Individual.objects.get(UID=patient)
    treatments = Treatment.objects.filter(Patient=p)
    return ("treatments.html"
        , {"first_name" : p.FirstName
         , "last_name" : p.LastName
         , "treatments" : treatments})

@login_required
@request_wrapper
@jeeves
def diagnoses_view(request, profile, patient):
    """Diagnoses.
    """
    p = Individual.objects.get(UID=patient)
    newDiagnoses = Diagnosis.objects.filter(Patient=p)
    diagnoses = [
         {"Manifestation" : "A38.8"
        , "DateRecognized" : date(2012, 10, 17)
        , "RecognizingEntity" : {"Name" : "Solomon Health", "ID" : 7}
        , "Diagnosis" : "Negative"}
      , {"Manifestation" : "E54"
        , "DateRecognized" : date(2012, 11, 24)
        , "RecognizingEntity" : {"Name" : "Cragley Medical National", "ID" : 98}
        , "Diagnosis" : "Negative"}
      , {"Manifestation" : "B01.0"
        , "DateRecognized" : date(2013, 2, 1)
        , "RecognizingEntity" : {"Name" : "Southwest Hospital", "ID" : 1}
        , "Diagnosis" : "Negative"}
      , {"Manifestation" : "T84.012"
        , "DateRecognized" : date(2013, 10, 17)
        , "RecognizingEntity" : {"Name" : "Dr. Wragley Medical Center"
                                , "ID" : 130}
      , "Diagnosis" : "Positive"}]
    return ("diagnoses.html"
            , {"first_name" : p.FirstName
             , "last_name" : p.LastName
             , "diagnoses" : newDiagnoses})

@login_required
@request_wrapper
@jeeves
def info_view(request, profile, patient):
    """Viewing information about an individual.
    """
    p = Individual.objects.get(UID=patient)
    dataset = []
    dataset.append(("Sex", p.Sex, False))
    #print "HI"
    #dataset.append(("Address",p.Address.String(), False))
    #dataset.append(("Social Security Number",p.SSN))
    return ("info.html"
            , {"patient": p
             , "dataset": dataset})

@login_required
@request_wrapper
@jeeves
def directory_view(request, profile, entity):
    """Viewing covered entities.
    """
    entity = CoveredEntity.objects.get(EIN=entity)
    visits = entity.Patients.filter(DateReleased=None)
    
    oldVisits = [
           {"Patient" : {"Name" : "Joe McGray", "ID" : 5}
          , "DateAdmitted" : date(2014, 5, 25)
          , "Location" : "113B"
          , "Condition" : "Recovering"
          , "ReligiousAffiliation" : "None"}
        , {"Patient" : {"Name" : "Briann Terack", "ID" : 52}
          , "DateAdmitted" : date(2014, 3, 30)
          , "Location" : "416"
          , "Condition" : "Severe"
          , "ReligiousAffiliation" : "Catholic"}
        , {"Patient" : {"Name" : "Henry Bion", "ID" : 95}
          , "DateAdmitted" : date(2014, 5, 12)
          , "Location" : "134K"
          , "Condition" : "Stable"
          , "ReligiousAffiliation" : "Christian"}
        , {"Patient" : {"Name" : "Gill Hansen", "ID" : 13}
          , "DateAdmitted" : date(2014, 5, 19)
          , "Location" : "228"
          , "Condition" : "Unknown"
          , "ReligiousAffiliation" : "Christian"}]
    return ("directory.html"
            , {"entity":entity, "visits":visits})

@login_required
@request_wrapper
@jeeves
def transactions_view(request, profile, entity):
    """
    Viewing transactions.
    """
    entity = CoveredEntity.objects.get(EIN=entity)
    transactions = Transaction.objects.filter(FirstParty=entity)
    other_transactions = Transaction.objects.filter(SecondParty=entity)
    return ("transactions.html"
            , {"entity": entity
             , "transactions":transactions
             , "other_transactions": other_transactions})

@login_required
@request_wrapper
@jeeves
def associates_view(request, profile, entity):
    entity = CoveredEntity.objects.get(EIN=entity)
    associates = entity.Associations.all()
    # TODO: Do something with this old_associates
    old_associates = [
          {"Entity" : {"Name" : "Cooper United"}
          , "InformationShared" : INFORMATION_SET
          , "Purpose" : "Files paperwork regarding hospital transfers."}
        , {"Entity" : {"Name" : "Sand Way", "ID" : 901}
          , "InformationShared" : INFORMATION_SET
          , "Purpose":"Billing"}
        , {"Entity" : {"Name" : "Handerson"}
          , "InformationShared" : INFORMATION_SET
          , "Purpose":"Keeps records for HIPAA audit"}]
    return ("associates.html"
        , {"entity":entity, "associates":associates})
