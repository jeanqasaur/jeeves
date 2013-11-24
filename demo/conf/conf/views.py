from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User

import forms

from models import Paper, PaperVersion, UserProfile, Review

def register_account(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("index")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = forms.ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            profile = UserProfile()
            profile.user = user
            profile_form = forms.ProfileForm(request.POST, instance=profile)
            profile_form.save()

            user = authenticate(username=request.POST['username'],
                         password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()
        profile_form = forms.ProfileForm()

    return render_to_response("registration/account.html", RequestContext(request,
        {
            'form' : form,
            'profile_form' : profile_form,
        }))

@login_required
def index(request):
    return render_to_response("index.html", RequestContext(request))

@login_required
def paper_view(request):
    try:
        paper = Paper.objects.filter(id=int(request.GET['id'])).get()
        paper_versions = list(PaperVersion.objects.filter(paper=paper).order_by('-time').all())
        authors = paper.authors.all()
        latest_abstract = paper_versions[-1].abstract if paper_versions else None
        reviews = list(Review.objects.filter(paper=paper).order_by('-time').all())
    except Paper.DoesNotExist:
        paper = None
        paper_versions = []
        authors = []
        latest_abstract = None
        reviews = []

    return render_to_response("paper.html", RequestContext(request, {
        'paper' : paper,
        'paper_versions' : paper_versions,
        'authors' : authors,
        'latest_abstract' : latest_abstract,
        'reviews' : reviews,
    }))

@login_required
def submit_view(request):
    if request.method == 'POST':
        form = forms.SubmitForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(request.user)
            return HttpResponseRedirect("paper?id=%d" % paper.id)
    else:
        form = forms.SubmitForm()

    return render_to_response("submit.html", RequestContext(request, {'form' : form}))

@login_required
def profile_view(request):
    try:
        profile = UserProfile.objects.filter(user=request.user).get()
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        if not profile:
            profile = UserProfile()
            profile.user = request.user
        form = forms.ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = forms.ProfileForm(instance=profile)

    return render_to_response("profile.html", RequestContext(request, {'form' : form}))

@login_required
def submit_review_view(request):
    try:
        if request.method == 'GET':
            paper_id = int(request.GET['id'])
        elif request.method == 'POST':
            paper_id = int(request.POST['id'])
        paper = Paper.objects.filter(id=paper_id).get()
        review = Review()
        review.paper = paper
        review.reviewer = request.user
        if request.method == 'POST':
            form = forms.SubmitReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save(paper)
                return HttpResponseRedirect("paper?id=%d" % paper_id)
        else:
            form = forms.SubmitReviewForm()
    except (ValueError, KeyError, Paper.DoesNotExist):
        import traceback
        print traceback.format_exc()
        paper = None
        form = None

    return render_to_response("submit_review.html", RequestContext(request, {
        'form' : form,
        'paper' : paper,
    }))
