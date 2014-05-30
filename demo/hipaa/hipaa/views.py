from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.views import generic
from datetime import date
import urllib
import random

import forms

from models import Paper, PaperVersion, UserProfile, Review, ReviewAssignment, Comment, UserPCConflict, PaperCoauthor, PaperPCConflict

from sourcetrans.macro_module import macros, jeeves
import JeevesLib
informationSet = {
	"preview" : "5 regarding Joe McGray",
	"treatments" : [
		{
			"Patient" : 
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"Service" : "ADA:D4211",
			"DatePerformed" : date(2012,6,26),
			"PrescribingEntity" : 
			{
				"Name" : "Cooper Base Dental",
				"ID" : 5
			},
			"PerformingEntity" : 
			{
				"Name" : "Cooper Base Dental",
				"ID" : 5
			},
		},
		{
			"Patient" : 
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"Service" : "D7287",
			"DatePerformed" : date(2013,1,3),
			"PrescribingEntity" : 
			{
				"Name" : "Beautiful Smile",
				"ID" : 23
			},
			"PerformingEntity" : 
			{
				"Name" : "Mary Orman, DDS",
				"ID" : 942
			},
		}
	],
	"diagnoses" : [
		{
			"Patient" : 
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"Manifestation" : "B01.0",
			"DateRecognized" : date(2013,2,1),
			"RecognizingEntity" : 
			{
				"Name" : "Solomon Health",
				"ID" : 7
			},
			"Diagnosis" : "Negative"
		},
		{
			"Patient" : 
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"Manifestation" : "T84.012",
			"DateRecognized" : date(2013,10,17),
			"RecognizingEntity" : 
			{
				"Name" : "Dr. Wragley Medical Center",
				"ID" : 130
			},
			"Diagnosis" : "Positive"
		}
	],
	"hospitalVisits" : [
		{
			"Patient" : 
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"DateAdmitted" : date(2014,5,25),
			"Location" : "113B",
			"Condition" : "Recovering",
			"ReligiousAffiliation" : "None"
		}
	]
}
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
                name=request.POST.get('name',''),
                affiliation=request.POST.get('affiliation',''),
                level='normal',
                email=request.POST.get('email', ''),
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

@jeeves
def add_to_context(context_dict, request, template_name, profile, concretize):
    template_name = concretize(template_name)
    context_dict['concretize'] = concretize

    context_dict['is_admin'] = profile != None and profile.level == "chair"
    context_dict['profile'] = profile

    context_dict['is_logged_in'] = (request.user and
                                    request.user.is_authenticated() and
                                    (not request.user.is_anonymous()))

def request_wrapper(view_fn):
    def real_view_fn(request):
        try:
            ans = view_fn(request)
            template_name = ans[0]
            context_dict = ans[1]

            profile = UserProfile.objects.get(username=request.user.username)

            if template_name == "redirect":
                path = context_dict
                return HttpResponseRedirect(JeevesLib.concretize(profile, path))

            concretizeState = JeevesLib.jeevesState.policyenv.getNewSolverState(profile)
            def concretize(val):
                return concretizeState.concretizeExp(val, JeevesLib.jeevesState.pathenv.getEnv())
            #concretize = lambda val : JeevesLib.concretize(profile, val)
            add_to_context(context_dict, request, template_name, profile, concretize)

            #print 'concretized is', concretize(context_dict['latest_title'])

            return render_to_response(template_name, RequestContext(request, context_dict))

        except Exception:
            import traceback
            traceback.print_exc()
            raise

    real_view_fn.__name__ = view_fn.__name__
    return real_view_fn

@login_required
@request_wrapper
@jeeves
def index(request):
	user = UserProfile.objects.get(username=request.user.username)
	data = {
		"patients":
		[
			{
				"Name" : "Joe McGray",
				"ID" : 5 
			},
			{
				"Name" : "Leo Vanes",
				"ID" : 41
			},
			{
				"Name" : "Briann Terack",
				"ID" : 52
			},
			{
				"Name" : "Henry Bion",
				"ID" : 95
			},
			{
				"Name" : "Gill Hansen",
				"ID" : 13
			},
		],
		"entities":
		[
			{
				"Name" : "Cooper Base Dental",
				"ID" : 5
			},
			{
				"Name" : "Solomon Health",
				"ID" : 7
			},
			{
				"Name" : "Dr. Wragley Medical Center",
				"ID" : 130
			},
			{
				"Name" : "Mary Orman, DDS",
				"ID" : 942
			},
			{
				"Name" : "Beautiful Smile",
				"ID" : 23
			},
		],
		'name' : user.name,
	}
	return (   "index.html" , data)

@request_wrapper
@jeeves
def about_view(request):
  return ( "about.html"
         , { 'which_page' : "about" } )


def set_random_name(contents):
    contents.name = '%030x' % random.randrange(16**30) + ".pdf"

@login_required
@request_wrapper
@jeeves
def profile_view(request):
    profile = UserProfile.objects.get(username=request.user.username)
    if profile == None:
        profile = UserProfile(username=request.user.username)
        profile.level = 'normal'
    pcs = UserProfile.objects.filter(level='pc').all()
    
    if request.method == 'POST':
        profile.name = request.POST.get('name', '')
        profile.affiliation = request.POST.get('affiliation', '')
        profile.acm_number = request.POST.get('acm_number', '')
        profile.email = request.POST.get('email', '')
        profile.save()

        UserPCConflict.objects.filter(user=profile).delete()
        pc_conflicts = []
        for conf in request.POST.getlist('pc_conflicts[]'):
            new_pc_conflict = UserProfile.objects.get(username=conf)
            UserPCConflict.objects.create(user=profile, pc=new_pc_conflict)
            pc_conflicts.append(new_pc_conflict)
    else:
        pc_conflicts = [uppc.pc for uppc in UserPCConflict.objects.filter(user=profile).all()]

    return ("profile.html", {
        "name": profile.name,
        "affiliation": profile.affiliation,
        "acm_number": profile.acm_number,
        "pc_conflicts": pc_conflicts,
        "email": profile.email,
        "pcs": pcs,
        "which_page": "profile",
        "pcs": [{'pc':pc, 'conflict':pc in pc_conflicts} for pc in pcs],
    })

@login_required
@request_wrapper
@jeeves
def users_view(request):
    user = UserProfile.objects.get(username=request.user.username)
    if user.level != 'chair':
        return (   "redirect", "/index")

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
        'which_pages' : "users"
    })

@login_required
def search_view(request):
    # TODO choose the actual set of possible reviewers
    possible_reviewers = list(User.objects.all())
    possible_authors = list(User.objects.all())

    form = forms.SearchForm(request.GET, reviewers=possible_reviewers, authors=possible_authors)
    if form.is_valid():
        results = form.get_results()
    else:
        results = []

    return render_to_response("search.html", RequestContext(request, {
        'form' : form,
        'results' : results,
        'which_page' : "search"
    }))

def treatments_view(request, patient):
	treatments = [
		{
			"Service" : "021009W",
			"DatePerformed" : date(2012,4,12),
			"PrescribingEntity" : 
			{
				"Name" : "West Health",
				"ID" : 710
			},
			"PerformingEntity" : 
			{
				"Name" : "Enlit Surgical",
				"ID" : 84
			},
		},
		{
			"Service" : "ADA:D4211",
			"DatePerformed" : date(2012,6,26),
			"PrescribingEntity" : 
			{
				"Name" : "Cooper Base Dental",
				"ID" : 5
			},
			"PerformingEntity" : 
			{
				"Name" : "Cooper Base Dental",
				"ID" : 5
			},
		},
		{
			"Service" : "D7287",
			"DatePerformed" : date(2013,1,3),
			"PrescribingEntity" : 
			{
				"Name" : "Beautiful Smile",
				"ID" : 23
			},
			"PerformingEntity" : 
			{
				"Name" : "Mary Orman, DDS",
				"ID" : 942
			},
		},
		{
			"Service" : "D2970",
			"DatePerformed" : date(2013,3,2),
			"PrescribingEntity" : 
			{
				"Name" : "Samuel Borndi, DMD",
				"ID" : 29
			},
			"PerformingEntity" : 
			{
				"Name" : "Enlit Surgical",
				"ID" : 84
			},
		}
	]
	return render_to_response("treatments.html", RequestContext(request, {"treatments":treatments}))

def diagnoses_view(request, patient):
	diagnoses = [
		{
			"Manifestation" : "A38.8",
			"DateRecognized" : date(2012,10,17),
			"RecognizingEntity" : 
			{
				"Name" : "Solomon Health",
				"ID" : 7
			},
			"Diagnosis" : "Negative"
		},
		{
			"Manifestation" : "E54",
			"DateRecognized" : date(2012,11,24),
			"RecognizingEntity" : 
			{
				"Name" : "Cragley Medical National",
				"ID" : 98
			},
			"Diagnosis" : "Negative"
		},
		{
			"Manifestation" : "B01.0",
			"DateRecognized" : date(2013,2,1),
			"RecognizingEntity" : 
			{
				"Name" : "Southwest Hospital",
				"ID" : 1
			},
			"Diagnosis" : "Negative"
		},
		{
			"Manifestation" : "T84.012",
			"DateRecognized" : date(2013,10,17),
			"RecognizingEntity" : 
			{
				"Name" : "Dr. Wragley Medical Center",
				"ID" : 130
			},
			"Diagnosis" : "Positive"
		}
    ]
	return render_to_response("diagnoses.html", RequestContext(request, {"diagnoses":diagnoses}))

def info_view(request, patient):
	dataset = [
		("Name","John H. Doe", True),
		("Gender","Male", False),
		("Birth Date", date(1986,4,3), False),
		("Address","42 Granite Way, Vineville, MI, 42459", False),
		("Telephone Number","729-555-4708", False),
		("Fax Number","939-555-1439", False),
		("Social Security Number","219-09-9999", False),
		("Driver's License Number","2549305480", False),
		("Email","jdoe8643@example.org", False),
		("Employer","Macro Creations Inc.", False),
	]
	print patient
	return render_to_response("info.html", RequestContext(request, {"dataset":dataset}))
def directory_view(request, entity):
	patients = [
		{
			"Patient" :
			{
				"Name" : "Joe McGray",
				"ID" : 5
			},
			"DateAdmitted" : date(2014,5,25),
			"Location" : "113B",
			"Condition" : "Recovering",
			"ReligiousAffiliation" : "None"
		},
		{
			"Patient" :
			{
				"Name" : "Briann Terack",
				"ID" : 52
			},
			"DateAdmitted" : date(2014,3,30),
			"Location" : "416",
			"Condition" : "Severe",
			"ReligiousAffiliation" : "Catholic"
		},
		{
			"Patient" :
			{
				"Name" : "Henry Bion",
				"ID" : 95
			},
			"DateAdmitted" : date(2014,5,12),
			"Location" : "134K",
			"Condition" : "Stable",
			"ReligiousAffiliation" : "Christian"
		},
		{
			"Patient" :
			{
				"Name" : "Gill Hansen",
				"ID" : 13
			},
			"DateAdmitted" : date(2014,5,19),
			"Location" : "228",
			"Condition" : "Unknown",
			"ReligiousAffiliation" : "Christian"
		}
    ]
	return render_to_response("directory.html", RequestContext(request, {"patients":patients}))
def transactions_view(request, entity):
	transactions = [
		{
			"Standard" : "ASC X12N 837",
			"OtherEntity" : 
			{
				"Name" : "Green America Professional",
				"ID" : 49
			},
			"InformationShared" : informationSet,
			"DateRequested" : date(2014, 4, 3),
			"DateResponded" : date(2014, 4, 8),
			"Purpose" : "Claims for medical procedures"
		},
		{
			"Standard" : "ASC X12N 270",
			"OtherEntity" : 
			{
				"Name" : "Green America Professional",
				"ID" : 49
			},
			"InformationShared" : informationSet,
			"DateRequested" : date(2014, 4, 10),
			"DateResponded" : date(2014, 4, 18),
			"Purpose" : "Benefit information inquiry"
		}
	]
	return render_to_response("transactions.html", RequestContext(request, {"transactions":transactions}))
def associates_view(request, entity):
	associates = [
		{
			"Entity" : 
			{
				"Name" : "Cooper United",
			},
			"InformationShared" : informationSet,
			"Purpose" : "Files paperwork regarding hospital transfers."
		},
		{
			"Entity" : 
			{
				"Name" : "Sand Way",
				"ID" : 901
			},
			"InformationShared":informationSet,
			"Purpose":"Billing",
		},
		{
			"Entity" : 
			{
				"Name" : "Handerson"
			},
			"InformationShared":informationSet,
			"Purpose":"Keeps records for HIPAA audit"
		}
	]
	return render_to_response("associates.html", RequestContext(request, {"associates":associates}))