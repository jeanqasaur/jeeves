from django.forms import Form, ModelForm, CharField, FileField, Textarea, ModelForm, HiddenInput

from models import Paper, PaperVersion, UserProfile, Review, ReviewAssignment
from django.contrib.auth.models import User
import random
from django.forms.formsets import formset_factory

class SubmitForm(Form):
    coauthor1 = CharField(required=False)
    coauthor2 = CharField(required=False)
    coauthor3 = CharField(required=False)

    title = CharField(1024, required=True)
    contents = FileField(required=True)
    abstract = CharField(widget=Textarea, required=True)

    def is_valid(self):
        if not super(SubmitForm, self).is_valid():
            print 'foo'
            return False

        try:
            coauthors = []
            for coauthor_id in ['coauthor1', 'coauthor2', 'coauthor3']:
                if coauthor_id in self.cleaned_data and self.cleaned_data[coauthor_id]:
                    coauthor = User.objects.filter(username=self.cleaned_data[coauthor_id]).get()
                    coauthors.append(coauthor)
        except User.DoesNotExist:
            print 'moo'
            return False

        self.cleaned_data['coauthors'] = coauthors
        return True

    def save(self, user):
        d = self.cleaned_data
        
        authors = [user]
        if 'coauthor1' in d:
            authors.append(d['coauthor1'])
        if 'coauthor2' in d:
            authors.append(d['coauthor2'])
        if 'coauthor3' in d:
            authors.append(d['coauthor3'])

        paper = Paper()
        paper.save()

        paper.authors.add(user)
        for coauthor in d['coauthors']:
            paper.authors.add(coauthor)
        paper.save()

        d['contents'].name = '%030x' % random.randrange(16**30) + ".pdf"

        paper_version = PaperVersion(
            paper = paper,
            title = d['title'],
            abstract = d['abstract'],
            contents = d['contents'],
        )
        paper_version.save()

        return paper

class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        # TODO pc_conflicts should only have PC members
        fields = ['name', 'affiliation', 'acm_number', 'pc_conflicts']

class SubmitReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'score_novelty', 'score_presentation', 'score_technical', 'score_confidence']

class ReviewAssignmentForm(ModelForm):
    class Meta:
        model = ReviewAssignment
        fields = ['type', 'user', 'paper']
        widgets = {
            'user' : HiddenInput(),
            'paper' : HiddenInput(),
        }

ReviewAssignmentFormset = formset_factory(ReviewAssignmentForm, extra=0)
