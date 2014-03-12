from django.forms import Form, ModelForm, CharField, FileField, Textarea, ModelForm, HiddenInput, MultipleChoiceField, CheckboxSelectMultiple, BooleanField, ChoiceField

from models import Paper, PaperVersion, UserProfile, Review, ReviewAssignment, Comment, UserPCConflict
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

    def __init__(self, possible_reviewers, default_conflict_reviewers, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)

        choices = []
        for r in possible_reviewers:
            choices.append((r.username, r))

        self.fields['conflicts'] = MultipleChoiceField(widget=CheckboxSelectMultiple(), required=False, choices=choices, initial=list(default_conflict_reviewers))

    def is_valid(self):
        if not super(SubmitForm, self).is_valid():
            return False

        try:
            coauthors = []
            for coauthor_id in ['coauthor1', 'coauthor2', 'coauthor3']:
                if coauthor_id in self.cleaned_data and self.cleaned_data[coauthor_id]:
                    coauthor = User.objects.filter(username=self.cleaned_data[coauthor_id]).get()
                    coauthors.append(coauthor)
        except User.DoesNotExist:
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

        # need to save paper twice since paper and paper_version point to each other...
        paper.latest_version = paper_version
        paper.save()

        for conflict_username in d['conflicts']:
            ra = ReviewAssignment()
            ra.user = User.objects.get(username=conflict_username)
            ra.paper = paper
            ra.type = 'conflict'
            ra.save()

        return paper

class SubmitReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['contents', 'score_novelty', 'score_presentation', 'score_technical', 'score_confidence']

class SubmitCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['contents']

class ReviewAssignmentForm(ModelForm):
    class Meta:
        model = ReviewAssignment
        fields = ['type', 'user', 'paper']
        widgets = {
            'user' : HiddenInput(),
            'paper' : HiddenInput(),
        }

ReviewAssignmentFormset = formset_factory(ReviewAssignmentForm, extra=0)

class SearchForm(Form):
    # should only show accepted papers
    filter_accepted = BooleanField(required=False)

    # should only show papers accepted by a reviewer
    # filter_reviewer (defined in __init__ below)

    # should only show papers by the given author
    # filter_author (defined in __init__ below)

    filter_title_contains = CharField(required=False)

    sort_by = ChoiceField(required=True,
                            choices=(('---', None),
                                     ('title', 'title'),
                                     ('score_technical', 'score_technical'),
                                    ))

    def __init__(self, *args, **kwargs):
        reviewers = kwargs['reviewers']
        authors = kwargs['authors']
        del kwargs['reviewers']
        del kwargs['authors']

        super(SearchForm, self).__init__(*args, **kwargs)
        
        self.fields['filter_reviewer'] = ChoiceField(required=False,
            choices=[('', '---')] + [(r.username, r) for r in reviewers])
        self.fields['filter_author'] = ChoiceField(required=False,
            choices=[('', '---')] + [(r.username, r) for r in authors])

    def get_results(self):
        d = self.cleaned_data

        query = Paper.objects

        # TODO enable support for accepting papers and then enable this
        #if d['filter_accepted']:
        #    query = query.filter(

        if d.get('filter_reviewer', ''):
            query = query.filter(authors__username=d['filter_reviewer'])

        if d.get('filter_author', ''):
            query = query.filter(reviewers__username=d['filter_author'])

        if d.get('filter_title_contains', ''):
            query = query.filter(latest_version__title__contains=d['filter_title_contains'])

        if d.get('sort_by','') == 'title':
            query = query.order_by('latest_version__title')
        elif d.get('sort_by','') == 'score_technical':
            query = query.order_by('latest_version__score_technical')

        print query.query.__str__()
        results = list(query.all())

        return list(results)
