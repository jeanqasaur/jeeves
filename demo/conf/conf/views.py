from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

def register_account(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("index")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect("index")
    else:
        form = UserCreationForm()

    return render_to_response("registration/account.html", RequestContext(request, {'form' : form}))

#def logout_view(request):
#    logout(request)
#        return HttpResponseRedirect("account")

@login_required
def index(request):
    return HttpResponseRedirect("index.html")

@login_required
def paper_view(request):
    pass

@login_required
def submit_view(request):
    pass
