from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField, BooleanField

from jeevesdb.JeevesModel import JeevesModel as Model
from jeevesdb.JeevesModel import JeevesForeignKey as ForeignKey

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

    @staticmethod
    def jeeves_get_private_user(uppc):
        return None
    @staticmethod
    def jeeves_get_private_pc(uppc):
        return None

    @staticmethod
    def jeeves_restrict_user(uppc, ctxt):
        return uppc.user == ctxt
    @staticmethod
    def jeeves_restrict_pc(uppc, ctxt):
        return uppc.user == ctxt

class Paper(Model):
    #latest_version = ForeignKey('PaperVersion', related_name='latest_version_of', null=True)
    # add this below because of cyclic dependency; awkward hack
    # (limitation of JeevesModel not ordinary Model)
    author = ForeignKey(UserProfile)

    accepted = BooleanField()

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
