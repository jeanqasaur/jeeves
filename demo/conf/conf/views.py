from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
import urllib
import random

import forms

from models import Paper, PaperVersion, UserProfile, Review, ReviewAssignment, Comment, UserPCConflict, PaperCoauthor, PaperPCConflict

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

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

def request_wrapper(view_fn):
    def real_view_fn(request):
        try:
            (template_name, context_dict) = view_fn(request)
        except Exception:
            import traceback
            traceback.print_exc()
            raise

        if template_name == "redirect":
            path = context_dict
            return HttpResponseRedirect(path)

        template_name = JeevesLib.concretize(request.user, template_name)
        concretize = lambda val : JeevesLib.concretize(request.user, val)
        context_dict['concretize'] = concretize
        return render_to_response(template_name, RequestContext(request, context_dict))
    real_view_fn.__name__ = view_fn.__name__
    return real_view_fn

@login_required
def index(request):
    return render_to_response("index.html", RequestContext(request))

@login_required
@request_wrapper
@jeeves
def paper_view(request):
    paper = Paper.objects.get(jeeves_id=request.GET.get('id', ''))
    if paper != None:
        paper_versions = PaperVersion.objects.filter(paper=paper).order_by('-time').all()
        coauthors = PaperCoauthor.objects.filter(paper=paper).all()
        latest_abstract = paper_versions[-1].abstract if len(paper_versions) > 0 else None
        latest_title = paper_versions[-1].title if len(paper_versions) > 0 else None
        reviews = Review.objects.filter(paper=paper).order_by('-time').all()
        comments = Comment.objects.filter(paper=paper).order_by('-time').all()
        author = UserProfile.objects.get(user=request.user)
    else:
        paper = None
        paper_versions = []
        coauthors = []
        latest_abstract = None
        latest_title = None
        reviews = []
        comments = []

    return ("paper.html", {
        'paper' : paper,
        'paper_versions' : paper_versions,
        'author' : author,
        'coauthors' : coauthors,
        'latest_abstract' : latest_abstract,
        'latest_title' : latest_title,
        'reviews' : reviews,
        'comments' : comments,
    })

def set_random_name(contents):
    contents.name = '%030x' % random.randrange(16**30) + ".pdf"

@login_required
@request_wrapper
@jeeves
def submit_view(request):
    if request.method == 'POST':
        coauthors = request.POST.getlist('coauthors[]')
        title = request.POST.get('title', None)
        abstract = request.POST.get('abstract', None)
        contents = request.FILES.get('contents', None)

        if title == None or abstract == None or contents == None:
            return ("submit.html", {
                'coauthors' : coauthors,
                'title' : title,
                'abstract' : abstract,
                'contents' : contents.name,
                'error' : 'Please fill out all fields'
            })

        paper = Paper.objects.create(author=request.user)
        for coauthor in coauthors:
            if coauthor != "":
                PaperCoauthor.objects.create(paper=paper, author=coauthor)
        set_random_name(contents)
        PaperVersion.objects.create(
            paper=paper,
            title=title,
            abstract=abstract,
            contents=contents
        )

        for conf in request.POST.getlist('pc_conflicts[]'):
            new_pc_conflict = User.objects.get(username=conf)
            PaperPCConflict.objects.create(paper=paper, pc=new_pc_conflict)

        return ("redirect", "paper?id=%s" % paper.jeeves_id)

    pcs = User.objects.all()
    pc_conflicts = [uppc.pc for uppc in UserPCConflict.objects.filter(user=request.user)]
    
    return ("submit.html", {
        'coauthors' : [],
        'title' : '',
        'abstract' : '',
        'contents' : '',
        'error' : '',
        'pcs' : pcs,
        'pc_conflicts' : pc_conflicts,
    })

@login_required
@request_wrapper
@jeeves
def profile_view(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    if profile == None:
        profile = UserProfile(user=user)
        profile.level = 'normal'
    pcs = User.objects.all()
    
    if request.method == 'POST':
        profile.name = request.POST.get('name', '')
        profile.affiliation = request.POST.get('affiliation', '')
        profile.acm_number = request.POST.get('acm_number', '')
        profile.save()

        UserPCConflict.objects.filter(user=user).delete()
        pc_conflicts = []
        for conf in request.POST.getlist('pc_conflicts[]'):
            new_pc_conflict = User.objects.get(username=conf)
            UserPCConflict.objects.create(user=user, pc=new_pc_conflict)
            pc_conflicts.append(new_pc_conflict)
    else:
        pc_conflicts = [uppc.pc for uppc in UserPCConflict.objects.filter(user=user)]

    return ("profile.html", {
        "name": profile.name,
        "affiliation": profile.affiliation,
        "acm_number": profile.acm_number,
        "pc_conflicts": pc_conflicts,
        "pcs": pcs,
    })

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
                return HttpResponseRedirect("paper?id=%s" % paper_id)
        else:
            form = forms.SubmitReviewForm()
    except (ValueError, KeyError, Paper.DoesNotExist):
        paper = None
        form = None

    return render_to_response("submit_review.html", RequestContext(request, {
        'form' : form,
        'paper' : paper,
    }))

@login_required
@request_wrapper
@jeeves
def users_view(request):
    user_profiles = UserProfile.objects.all()

    if request.method == 'POST':
        for profile in user_profiles:
            query_param_name = 'level-' + profile.user.username
            level = request.POST.get(query_param_name, '')
            if level in ['normal', 'pc', 'chair']:
                print 'HELLO'
                profile.level = level
                profile.save()

    return ("users_view.html", {
        'user_profiles': user_profiles,
    })

@login_required
def submit_comment_view(request):
    try:
        if request.method == 'GET':
            paper_id = int(request.GET['id'])
        elif request.method == 'POST':
            paper_id = int(request.POST['id'])
        paper = Paper.objects.filter(id=paper_id).get()
        comment = Comment()
        comment.paper = paper
        comment.user = request.user
        if request.method == 'POST':
            form = forms.SubmitCommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save(paper)
                return HttpResponseRedirect("paper?id=%s" % paper_id)
        else:
            form = forms.SubmitCommentForm()
    except (ValueError, KeyError, Paper.DoesNotExist):
        paper = None
        form = None

    return render_to_response("submit_comment.html", RequestContext(request, {
        'form' : form,
        'paper' : paper,
    }))

@login_required
def assign_reviews_view(request):
    possible_reviewers = list(User.objects.all()) # TODO filter by people who are reviewers

    reviewer = None
    try:
        reviewer_username = request.GET['reviewer_username']
        for r in possible_reviewers:
            if r.username == reviewer_username:
                reviewer = r
                break
    except KeyError:
        pass
    if not reviewer:
        reviewer = request.user

    papers = list(Paper.objects.all())
    assignments = list(ReviewAssignment.objects.filter(user=reviewer).all())

    # Construct initial_data which is a list of ReviewAssignments for
    # the ReviewAssignmentFormset. For the given user, we should have one
    # for each paper. If one does not already exist for some paper, create it.
    data = {assignment.paper : {
        'user' : assignment.user,
        'paper' : assignment.paper,
        'type' : assignment.type
      } for assignment in assignments}
    for paper in papers:
        if paper not in data:
            data[paper] = {
                'user' : reviewer,
                'paper' : paper,
                'type' : 'none'
            }
    initial_data = data.values()

    if request.method == 'POST':
        formset = forms.ReviewAssignmentFormset(request.POST, initial=initial_data)
        if formset.is_valid():
            for form in formset.forms:
                form.save()
            return HttpResponseRedirect("assign_reviews?reviewer_username=%s" % urllib.quote(reviewer.username))
    else:
        formset = forms.ReviewAssignmentFormset(initial=initial_data)

    return render_to_response("assign_reviews.html", RequestContext(request, {
        'reviewer' : reviewer,
        'formset' : formset,
        'possible_reviewers' : possible_reviewers,
    }))

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
    }))

def about_view(request):
  return render_to_response("about.html", RequestContext(request))
