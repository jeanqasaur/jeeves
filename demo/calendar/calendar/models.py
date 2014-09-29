from datetime import datetime
from django.db.models import CharField, DateTimeField
from jeevesdb.JeevesModel import JeevesModel as Model, JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

# An example model.
# Right now self-reference is either impossible or difficult because JeevesForeignKey
# only supports a model class (not a string) as the related object. (TODO fix this.)
class UserProfile(Model):
    username = CharField(max_length=256)
    email = CharField(max_length=256)

    @staticmethod
    def jeeves_get_private_email(user):
	return "[redacted]"

    @staticmethod
    @label_for('email')
    @jeeves
    def jeeves_restrict_userprofilelabel(user, ctxt):
        return user == ctxt

    @jeeves
    def has_event(self,event):
        return (EventGuest.objects.get(event=event, guest=self) != None) \
            or (EventHost.objects.get(event=event, host=self) != None)

class Event(Model):
    VISIBILITY = (('E', 'Everyone'), ('G', 'Guests' ))

    name = CharField(max_length=256)
    location = CharField(max_length=512)
    time = DateTimeField()
    description = CharField(max_length=1024)
    visibility = CharField(max_length=1, choices=VISIBILITY, default='E')

    @jeeves
    def has_host(self, host):
        return EventHost.objects.get(event=self, host=host) != None

    @jeeves
    def has_guest(self, guest):
        return EventGuest.objects.get(event=self, guest=guest) != None

    @staticmethod
    def jeeves_get_private_name(event):
        return "Private event"
    @staticmethod
    def jeeves_get_private_location(event):
        return "Undisclosed location"
    @staticmethod
    def jeeves_get_private_time(event):
        return datetime(1999, 1, 1, 0)
    @staticmethod
    def jeeves_get_private_description(event):
        return "An event."

    @staticmethod
    @label_for('name', 'location', 'time', 'description')
    @jeeves
    def jeeves_restrict_event(event, ctxt):
        if event.visibility == 'G':
            return event.has_host(ctxt) or event.has_guest(ctxt)
        else:
            return True

class EventHost(Model):
    """Relates events to hosts.
    """
    event = ForeignKey(Event, null=True)
    host = ForeignKey(UserProfile, null=True)

class EventGuest(Model):
    """Relates events to guests.
    """
    event = ForeignKey(Event, null=True)
    guest = ForeignKey(UserProfile, null=True)
