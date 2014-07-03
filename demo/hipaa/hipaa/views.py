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

from models import Individual, CoveredEntity, UserProfile, Transaction

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
			type=request.POST.get('type','')
			individual=None
			entity=None
			associate=None
			if type==1:
				(firstName, lastName) = profile.name.split(" ")
				individual = Individual.objects.get(FirstName=firstName, LastName=lastName)
			elif type==2:
				entity = CoveredEntity.objects.get(Name=profile.name)
			elif type==3:
				associate = BusinessAssociates.objects.get(Name=profile.name)

			UserProfile.objects.create(
			    username=user.username,
			    name=request.POST.get('name',''),			
			    email=request.POST.get('email', ''),
				individual=individual,
				entity=entity,
				associate=associate,
				type=type
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

    #context_dict['is_admin'] = profile != None and profile.level == "chair"
    context_dict['profile'] = profile

    context_dict['is_logged_in'] = (request.user and
                                    request.user.is_authenticated() and
                                    (not request.user.is_anonymous()))

def request_wrapper(view_fn):
    def real_view_fn(request, **kwargs):
        try:
            ans = view_fn(request,**kwargs)
            template_name = ans[0]
            context_dict = ans[1]

            profile = UserProfile.objects.get(user=request.user)

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
	patients = Individual.objects.all()
	entities = CoveredEntity.objects.all()
	data = {
		"patients": patients,
		"entities": entities,
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
	pcs = UserProfile.objects.all()
	if request.method == 'POST':
		profile.name = request.POST.get('name', '')
		profile.type=request.POST.get('type','')
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
    if user.type != 3:
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
	p = Individual.objects.get(UID=patient)
	treatments = p.treatment_set.all()
	return render_to_response("treatments.html", RequestContext(request, {"name" : p.Name(),"treatments" : treatments}))

def diagnoses_view(request, patient):
	p = Individual.objects.get(UID=patient)
	newDiagnoses = p.diagnosis_set.all()
	print len(newDiagnoses)
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
	return render_to_response("diagnoses.html", RequestContext(request, {"name":p.Name() , "diagnoses":newDiagnoses}))

@login_required
@request_wrapper
@jeeves
def info_view(request, patient):
	p = Individual.objects.get(UID=patient)
	dataset = []
	dataset.append(("Address",p.Address.String()))
	dataset.append(("Social Security Number",p.SSN))
	return ("info.html", {"patient":p,"dataset":dataset})
def directory_view(request, entity):
	entity = CoveredEntity.objects.get(EIN=entity)
	visits = entity.Patients.filter(DateReleased=None)
	oldVisits = [
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
	return render_to_response("directory.html", RequestContext(request, {"entity":entity, "visits":visits}))
def transactions_view(request, entity):
	entity = CoveredEntity.objects.get(EIN=entity)
	transactions = entity.SomeTransactions.all()
	for i in range(entity.MoreTransactions.count()):			#This is really bad code, (I'm not sure if we can assume all() will return the same
		transactions.append(entity.MoreTransactions.all()[i])	#ordering each call), but I can't see any other way with Jeeves.
	#for i in range(len(transactions)):
	#	transactions[i].TreatmentsShared = Transaction.SharedInformation.Treatments	
	return render_to_response("transactions.html", RequestContext(request, {"entity":entity, "transactions":transactions}))
def associates_view(request, entity):
	entity = CoveredEntity.objects.get(EIN=entity)
	associates = entity.Associations

	oldAssociates = [
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
	return render_to_response("associates.html", RequestContext(request, {"entity":entity, "associates":associates}))