import datetime
from django import forms

import models

class EventForm(forms.Form):
    VISIBILITY = (('E', 'Everyone'), ('G', 'Guests' ))

    name = forms.CharField(label='Name')
    location = forms.CharField()
    time = forms.DateField(initial=datetime.date.today)
    description = forms.CharField(widget=forms.Textarea)
    visibility = forms.ChoiceField(widget=forms.RadioSelect, choices=VISIBILITY)
