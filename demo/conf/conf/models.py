from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField, BooleanField

from jeevesdb.JeevesModel import JeevesModel as Model
from jeevesdb.JeevesModel import JeevesForeignKey as ForeignKey
from jeevesdb.JeevesModel import label_for

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

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
    def jeeves_get_private_email(user):
        return ""

    @staticmethod
    @label_for('email')
    @jeeves
    def jeeves_restrict_userprofilelabel(user, ctxt):
        return user == ctxt or ctxt.level == 'chair'

    class Meta:
        db_table = 'user_profiles'

class UserPCConflict(Model):
    user = ForeignKey(UserProfile, null=True, related_name='userpcconflict_user')
    pc = ForeignKey(UserProfile, null=True, related_name='userpcconflict_pc')

    @staticmethod
    def jeeves_get_private_user(uppc):
        return None
    @staticmethod
    def jeeves_get_private_pc(uppc):
        return None

    @staticmethod
    @label_for('user', 'pc')
    def jeeves_restrict_userpcconflictlabel(uppc, ctxt):
        return uppc == ctxt

class Paper(Model):
    #latest_version = ForeignKey('PaperVersion', related_name='latest_version_of', null=True)
    # add this below because of cyclic dependency; awkward hack
    # (limitation of JeevesModel not ordinary Model)
    author = ForeignKey(UserProfile, null=True)
    accepted = BooleanField()

    @staticmethod
    @jeeves
    def jeeves_get_private_author(paper):
        return None

    @staticmethod
    @label_for('author')
    @jeeves
    def jeeves_restrict_paperlabel(paper, ctxt):
        if phase == 'final':
            return True
        else:
            return (paper != None and paper.author == ctxt) or ctxt.level == 'chair'

    class Meta:
        db_table = 'papers'

class PaperPCConflict(Model):
    paper = ForeignKey(Paper, null=True)
    pc = ForeignKey(UserProfile, null=True)

class PaperCoauthor(Model):
    paper = ForeignKey(Paper, null=True)
    author = CharField(max_length=1024)

class PaperReviewer(Model):
    paper = ForeignKey(Paper, null=True)
    reviewer = ForeignKey(UserProfile, null=True)

class ReviewAssignment(Model):
    paper = ForeignKey(Paper, null=True)
    user = ForeignKey(UserProfile, null=True)
    assign_type = CharField(max_length=8, null=False,
        choices=(('none','none'),
                ('assigned','assigned'),
                ('conflict','conflict')))

    class Meta:
        db_table = 'review_assignments'

class PaperVersion(Model):
    paper = ForeignKey(Paper, null=True)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paper_versions'

    @staticmethod
    @jeeves
    @label_for('paper', 'title', 'contents', 'abstract')
    def jeeves_restrict_paperversionlabel(pv, ctxt):
        return (pv.paper != None and pv.paper.author == ctxt) or ctxt.level == 'pc' or ctxt.level == 'chair'
    
    @staticmethod
    def jeeves_get_private_paper(pv): return None
    @staticmethod
    def jeeves_get_private_title(pv): return ""
    @staticmethod
    def jeeves_get_private_contents(pv): return ""
    @staticmethod
    def jeeves_get_private_abstract(pv): return ""

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

    @staticmethod
    @label_for('paper', 'reviewer', 'contents', 'score_novelty', 'score_presentation', 'score_technical', 'score_confidence')
    @jeeves
    def jeeves_restrict_reviewlabel(review, ctxt):
        return ctxt.level == 'chair' or ctxt.level == 'pc' or \
                (phase == 'final' and review.paper.author == ctxt)

    class Meta:
        db_table = 'reviews'

class Comment(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper, null=True)
    user = ForeignKey(UserProfile, null=True)
    contents = TextField()

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
