from calendar.models import *
from django.contrib.auth.models import User
from datetime import date

aliceUser = UserProfile.objects.create(
    username="alice"
    , email="alice@mail.org")
alice=User.objects.create_user(
      username="alice"
    , email="alice@mail.org"
    , password="alice")

bobUser = UserProfile.objects.create(
    username="bob"
    , email="bob@mail.org")
bob=User.objects.create_user(
      username="bob"
    , email="bob@mail.org"
    , password="bob")

carolUser = UserProfile.objects.create(
    username="carol"
    , email="carol@mail.org")
carol=User.objects.create_user(
      username="carol"
    , email="carol@mail.org"
    , password="carol")

eveUser = UserProfile.objects.create(
    username="eve"
    , email="eve@mail.org")
eve=User.objects.create_user(
      username="eve"
    , email="eve@mail.org"
    , password="eve")

eveParty = Event.objects.create(
    name="Eve's surprise party"
    , location="Chuck E. Cheese's"
    , time=datetime(2014, 10, 24, 20, 0)
    , description="Don't tell Eve!"
    , visibility='G')

otherParty = Event.objects.create(
    name="Other party"
    , location="Other location"
    , time=datetime(2014, 10, 24, 20, 0)
    , description="Nothing of note.")

EventHost.objects.create(event=eveParty, host=aliceUser)
EventHost.objects.create(event=eveParty, host=bobUser)
EventGuest.objects.create(event=eveParty, guest=carolUser)
