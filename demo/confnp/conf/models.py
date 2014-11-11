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

    class Meta:
        db_table = 'papers'

class PaperPCConflict(Model):
    paper = ForeignKey(Paper, null=True)
    pc = ForeignKey(UserProfile, null=True)

class PaperCoauthor(Model):
    paper = ForeignKey(Paper, null=True)
    author = CharField(max_length=1024)

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

class PaperVersion(Model):
    paper = ForeignKey(Paper, null=True)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

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
