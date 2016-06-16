from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField, BooleanField

from settings import CONF_PHASE as phase

class UserProfile(Model):
    username = CharField(max_length=1024)
    email = CharField(max_length=1024)

    name = CharField(max_length=1024)
    affiliation = CharField(max_length=1024)
    acm_number = CharField(max_length=1024)

    level = CharField(max_length=12,
                    choices=(('normal', 'normal'),
                        ('pc', 'pc'),
                        ('chair', 'chair')))

    @staticmethod
    def get_private_email(user):
        return ""

    # Policy goes with email field.
    def policy_userprofilelabel(self, ctxt):
        return self == ctxt or (ctxt != None and ctxt.level == 'chair')

    class Meta:
        db_table = 'user_profiles'

class UserPCConflict(Model):
    user = ForeignKey(UserProfile, null=True, related_name='userpcconflict_user')
    pc = ForeignKey(UserProfile, null=True, related_name='userpcconflict_pc')

class Paper(Model):
    #latest_version = ForeignKey('PaperVersion', related_name='latest_version_of', null=True)
    # add this below because of cyclic dependency; awkward hack
    # (limitation of JeevesModel not ordinary Model)
    author = ForeignKey(UserProfile, null=True)
    accepted = BooleanField()

    @staticmethod
    def jeeves_get_private_author(paper):
        return None

    # Policy goes with author field.
    def policy_paperlabel(self, ctxt):
        '''
        Policy for seeing author of papers.
        '''
        if phase == 'final':
            return True
        else:
            # See if there is a PC conflict.
            try:
                conflict = PaperPCConflict.objects.get(paper=self, pc=ctxt)
                return False
            except:
                return ((self.author == ctxt)
                    or (ctxt != None and (ctxt.level == 'chair' or ctxt.level == 'pc')))

    class Meta:
        db_table = 'papers'

class PaperPCConflict(Model):
    paper = ForeignKey(Paper, null=True)
    pc = ForeignKey(UserProfile, null=True)

class PaperCoauthor(Model):
    paper = ForeignKey(Paper, null=True)
    author = CharField(max_length=1024)

    @staticmethod
    def jeeves_get_private_paper(pco): return None
    @staticmethod
    def jeeves_get_private_author(pco): return ""

    # Policy goes with paper and author fields.
    def jeeves_restrict_papercoauthorlabel(self, ctxt):
        if self.paper == None:
            return False
        else:
            try:
                PaperPCConflict.objects.get(paper=self.paper, pc=ctxt)
                return False
            except:
                return ctxt.level == 'pc' or ctxt.level == 'chair' or \
                    (self.paper != None and self.paper.author == ctxt)

#class PaperReviewer(Model):
#    paper = ForeignKey(Paper, null=True)
#    reviewer = ForeignKey(UserProfile, null=True)

#    @staticmethod
#    def jeeves_get_private_paper(pco): return None
#    @staticmethod
#    def jeeves_get_private_reviewer(pco): return None

#    @staticmethod
#    @label_for('paper', 'reviewer')
#    @jeeves
#    def jeeves_restrict_paperreviewerlabel(prv, ctxt):
#        return ctxt.level == 'pc' or ctxt.level == 'chair'

class ReviewAssignment(Model):
    paper = ForeignKey(Paper, null=True)
    user = ForeignKey(UserProfile, null=True)
    assign_type = CharField(max_length=8, null=True,
        choices=(('none','none'),
                ('assigned','assigned'),
                ('conflict','conflict')))

    class Meta:
        db_table = 'review_assignments'

    @staticmethod
    def jeeves_get_private_paper(rva): return None
    @staticmethod
    def jeeves_get_private_user(rva): return None
    @staticmethod
    def jeeves_get_private_assign_type(rva): return 'none'

    # Policy for paper, user, and assign_type fields.
    def jeeves_restrict_paperreviewerlabel(self, ctxt):
        try:
            PaperPCConflict.objects.get(paper=self.paper, pc=ctxt)
            return False
        except:
            return ctxt.level == 'pc' or ctxt.level == 'chair'

class PaperVersion(Model):
    paper = ForeignKey(Paper, null=True)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

    @staticmethod
    def jeeves_get_private_paper(pv): return None
    @staticmethod
    def jeeves_get_private_title(pv): return ""
    @staticmethod
    def jeeves_get_private_contents(pv): return ""
    @staticmethod
    def jeeves_get_private_abstract(pv): return ""

    # Policy for paper, title, contents, and abstract fields.
    def jeeves_restrict_paperversionlabel(self, ctxt):
        if self.paper == None:
            return False
        try:
            PaperPCConflict.objects.get(paper=self.paper, pc=ctxt)
            return False
        except:
            return (self.paper != None and self.paper.author == ctxt) or ctxt.level == 'pc' or ctxt.level == 'chair'

# see comment above
Paper.latest_version = ForeignKey(PaperVersion, related_name='latest_version_of', null=True)

class Tag(Model):
    name = CharField(max_length=32)
    paper = ForeignKey(Paper, null=True)

    class Meta:
        db_table = 'tags'

class Review(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper, null=True)
    reviewer = ForeignKey(UserProfile, null=True)
    contents = TextField()

    score_novelty = IntegerField()
    score_presentation = IntegerField()
    score_technical = IntegerField()
    score_confidence = IntegerField()

    @staticmethod
    def jeeves_get_private_paper(review): return None
    @staticmethod
    def jeeves_get_private_reviewer(review): return None
    @staticmethod
    def jeeves_get_private_contents(review): return ""
    @staticmethod
    def jeeves_get_private_score_novelty(review): return -1
    @staticmethod
    def jeeves_get_private_score_presentation(review): return -1
    @staticmethod
    def jeeves_get_private_score_technical(review): return -1
    @staticmethod
    def jeeves_get_private_score_confidence(review): return -1

    # Policy for paper, reviewer, contents, score_novelty, score_presentation,
    # score_tecincal, and score_confidence fields.
    def jeeves_restrict_reviewlabel(self, ctxt):
        try:
            PaperPCConflict.objects.get(paper=self.paper, pc=ctxt)
            return False
        except:
            return ctxt.level == 'chair' or ctxt.level == 'pc' or \
                (phase == 'final' and self.paper.author == ctxt)

    class Meta:
        db_table = 'reviews'

class Comment(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper, null=True)
    user = ForeignKey(UserProfile, null=True)
    contents = TextField()

    @staticmethod
    def jeeves_get_private_paper(review): return None
    @staticmethod
    def jeeves_get_private_user(review): return None
    @staticmethod
    def jeeves_get_private_contents(review): return ""

    # Policy for paper, user, and contents fields.
    def jeeves_restrict_reviewlabel(self, ctxt):
        if PaperPCConflict.objects.get(paper=self.paper, pc=ctxt) != None:
            return False
        return ctxt.level == 'chair' or ctxt.level == 'pc'

    class Meta:
        db_table = 'comments'

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser: 
        UserProfile.objects.create(
            username=instance.username,
            email=instance.email,
            level='chair',
        )
