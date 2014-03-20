from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField, BooleanField

from jeevesdb.JeevesModel import JeevesModel as Model
from jeevesdb.JeevesModel import JeevesForeignKey as ForeignKey

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
    @jeeves
    def jeeves_get_private_email(user):
        return ""
    @staticmethod
    @jeeves
    def jeeves_restrict_email(user, ctxt):
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
    def jeeves_restrict_user(uppc, ctxt):
        return uppc == ctxt
    @staticmethod
    def jeeves_restrict_pc(uppc, ctxt):
        return uppc == ctxt

class Paper(Model):
    #latest_version = ForeignKey('PaperVersion', related_name='latest_version_of', null=True)
    # add this below because of cyclic dependency; awkward hack
    # (limitation of JeevesModel not ordinary Model)
    author = ForeignKey(UserProfile)
    accepted = BooleanField()

    @staticmethod
    @jeeves
    def jeeves_get_private_author(paper):
        return None
    @staticmethod
    @jeeves
    def jeeves_restrict_author(paper, ctxt):
        if phase == 'final':
            return True
        else:
            return author == ctxt or ctxt.level == 'chair'

    class Meta:
        db_table = 'papers'

class PaperPCConflict(Model):
    paper = ForeignKey(Paper)
    pc = ForeignKey(UserProfile)

class PaperCoauthor(Model):
    paper = ForeignKey(Paper)
    author = CharField(max_length=1024)

class PaperReviewer(Model):
    paper = ForeignKey(Paper)
    reviewer = ForeignKey(UserProfile)

class ReviewAssignment(Model):
    paper = ForeignKey(Paper)
    user = ForeignKey(UserProfile)
    assign_type = CharField(max_length=8, null=False,
        choices=(('none','none'),
                ('assigned','assigned'),
                ('conflict','conflict')))

    class Meta:
        db_table = 'review_assignments'

class PaperVersion(Model):
    paper = ForeignKey(Paper)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paper_versions'
    
    @staticmethod
    def jeeves_get_private_paper(pv):
        return None
    @staticmethod
    @jeeves
    def jeeves_restrict_paper(pv, ctxt):
        return pv.paper.author == ctxt or ctxt.level == 'pc' or ctxt.level == 'chair'

    @staticmethod
    def jeeves_get_private_title(pv):
        return ""
    @staticmethod
    @jeeves
    def jeeves_restrict_title(pv, ctxt):
        return pv.paper.author == ctxt or ctxt.level == 'pc' or ctxt.level == 'chair'

    @staticmethod
    def jeeves_get_private_contents(pv):
        return ""
    @staticmethod
    @jeeves
    def jeeves_restrict_contents(pv, ctxt):
        return pv.paper.author == ctxt or ctxt.level == 'pc' or ctxt.level == 'chair'

    @staticmethod
    def jeeves_get_private_abstract(pv):
        return ""
    @staticmethod
    @jeeves
    def jeeves_restrict_abstract(pv, ctxt):
        return pv.paper.author == ctxt or ctxt.level == 'pc' or ctxt.level == 'chair'

# see comment above
Paper.latest_version = ForeignKey(PaperVersion, related_name='latest_version_of',)

class Tag(Model):
    name = CharField(max_length=32)
    paper = ForeignKey(Paper)

    class Meta:
        db_table = 'tags'

class Review(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper)
    reviewer = ForeignKey(UserProfile)
    contents = TextField()

    score_novelty = IntegerField()
    score_presentation = IntegerField()
    score_technical = IntegerField()
    score_confidence = IntegerField()

    @staticmethod
    def jeeves_get_private_paper(review):
        return None
    @staticmethod
    def jeeves_get_private_reviewer(review):
        return None
    @staticmethod
    def jeeves_get_private_contents(review):
        return ""
    @staticmethod
    def jeeves_get_private_score_novelty(review):
        return -1
    @staticmethod
    def jeeves_get_private_score_presentation(review):
        return -1
    @staticmethod
    def jeeves_get_private_score_technical(review):
        return -1
    @staticmethod
    def jeeves_get_private_score_confidence(review):
        return -1

    @staticmethod
    @jeeves
    def jeeves_restrict_paper(review, ctxt):
        return ctxt.level == 'chair' or ctxt.level == 'pc' or \
                (phase == 'final' and review.paper.author == ctxt)
    jeeves_restrict_reviewer = jeeves_restrict_paper
    jeeves_restrict_contents = jeeves_restrict_paper
    jeeves_restrict_score_novelty = jeeves_restrict_paper
    jeeves_restrict_score_presentation = jeeves_restrict_paper
    jeeves_restrict_score_technical = jeeves_restrict_paper
    jeeves_restrict_score_confidence = jeeves_restrict_paper

    class Meta:
        db_table = 'reviews'

class Comment(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper)
    user = ForeignKey(UserProfile)
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
