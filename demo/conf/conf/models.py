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
        return user == ctxt or (ctxt != None and ctxt.level == 'chair')

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
    @jeeves
    def jeeves_restrict_userpcconflictlabel(uppc, ctxt):
        return True
        #return ctxt.level == 'chair' or uppc.user == ctxt

class Paper(Model):
    #latest_version = ForeignKey('PaperVersion', related_name='latest_version_of', null=True)
    # add this below because of cyclic dependency; awkward hack
    # (limitation of JeevesModel not ordinary Model)
    author = ForeignKey(UserProfile, null=True)
    accepted = BooleanField()

    @staticmethod
    def jeeves_get_private_author(paper):
        return None

    @staticmethod
    @label_for('author')
    @jeeves
    def jeeves_restrict_paperlabel(paper, ctxt):
        '''
        Policy for seeing author of papers.
        '''
        if phase == 'final':
            return True
        else:
            if paper == None:
                return False
            if PaperPCConflict.objects.get(paper=paper, pc=ctxt) != None:
                return False

            # print "RESOLVING POLICY WITH PAPER: ", paper.id, ": ", paper.jeeves_id
            # print "RESOLVING POLICY WITH PAPER AUTHOR: ", paper.author.v
            r = ((paper != None and paper.author == ctxt)
                or (ctxt != None and (ctxt.level == 'chair' or ctxt.level == 'pc')))
            print r
            return r

    class Meta:
        db_table = 'papers'

class PaperPCConflict(Model):
    paper = ForeignKey(Paper, null=True)
    pc = ForeignKey(UserProfile, null=True)

    @staticmethod
    def jeeves_get_private_paper(ppcc): return None
    @staticmethod
    def jeeves_get_private_pc(ppcc): return None

    @staticmethod
    @label_for('paper', 'pc')
    @jeeves
    def jeeves_restrict_paperpcconflictlabel(ppcc, ctxt):
        return True
        #return ctxt.level == 'admin' or (ppcc.paper != None and ppcc.paper.author == ctxt)

class PaperCoauthor(Model):
    paper = ForeignKey(Paper, null=True)
    author = CharField(max_length=1024)

    @staticmethod
    def jeeves_get_private_paper(pco): return None
    @staticmethod
    def jeeves_get_private_author(pco): return ""

    @staticmethod
    @label_for('paper', 'author')
    @jeeves
    def jeeves_restrict_papercoauthorlabel(pco, ctxt):
        if pco.paper == None:
            return False
        if PaperPCConflict.objects.get(paper=pco.paper, pc=ctxt) != None:
            return False
        ans = ctxt.level == 'pc' or ctxt.level == 'chair' or (pco.paper != None and pco.paper.author == ctxt)
        return ans

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

    @staticmethod
    @label_for('paper', 'user', 'assign_type')
    @jeeves
    def jeeves_restrict_paperreviewerlabel(prv, ctxt):
        if prv != None and PaperPCConflict.objects.get(paper=prv.paper, pc=ctxt) != None:
            return False
        return ctxt.level == 'pc' or ctxt.level == 'chair'

class PaperVersion(Model):
    paper = ForeignKey(Paper, null=True)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paper_versions'

    @staticmethod
    @label_for('paper', 'title', 'contents', 'abstract')
    @jeeves
    def jeeves_restrict_paperversionlabel(pv, ctxt):
        if pv == None or pv.paper == None:
            return False
        if PaperPCConflict.objects.get(paper=pv.paper, pc=ctxt) != None:
            return False
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
        if review != None and PaperPCConflict.objects.get(paper=review.paper, pc=ctxt) != None:
            return False
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

    @staticmethod
    def jeeves_get_private_paper(review): return None
    @staticmethod
    def jeeves_get_private_user(review): return None
    @staticmethod
    def jeeves_get_private_contents(review): return ""

    @staticmethod
    @label_for('paper', 'user', 'contents')
    @jeeves
    def jeeves_restrict_reviewlabel(comment, ctxt):
        if comment != None and PaperPCConflict.objects.get(paper=comment.paper, pc=ctxt) != None:
            return False
        return ctxt.level == 'chair' or ctxt.level == 'pc'

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
