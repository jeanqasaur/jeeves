from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse

import forms, models

def register_account(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("index")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'],
                         password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()

    return render_to_response("registration/account.html", RequestContext(request, {'form' : form}))

@login_required
def index(request):
    return render_to_response("index.html", RequestContext(request))

@login_required
def paper_view(request):
    try:
        paper = models.Paper.objects().get(int(request.GET['id']))
    except Exception:
        paper = None

    return render_to_response("paper.html", RequestContext(request, {'paper' : paper}))

@login_required
def submit_view(request):
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST)
        if form.is_valid():
            paper = form.save()
            return HttpResponseRedirect("paper?id=%d" % paper.id)
    else:
        form = forms.ProfileForm()

    return render_to_response("profile.html", RequestContext(request, {'form' : form}))

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("accounts/profile")
    else:
        form = forms.ProfileForm()

    return render_to_response("profile.html", RequestContext(request, {'form' : form}))
