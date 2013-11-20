from django.db.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField, FileField
from django.contrib.auth.models import User

class UserProfile(Model):
    user = ForeignKey(User)
    name = CharField(max_length=1024)

    class Meta:
        db_table = 'user_profiles'

class Paper(Model):
    authors = ManyToManyField(User, related_name='authors')
    reviewers = ManyToManyField(User, related_name='reviewers')
    pc_conflicts = ManyToManyField(User, related_name='pc_conflicts')

    class Meta:
        db_table = 'papers'

class PaperVersion(Model):
    paper = ForeignKey(Paper)

    title = CharField(max_length=1024)
    contents = FileField(upload_to='papers')
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'paper_versions'

class Tag(Model):
    name = CharField(max_length=32)
    paper = ForeignKey(Paper)

    class Meta:
        db_table = 'tags'

class Review(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper)
    reviewer = ForeignKey(User)
    comment = TextField()

    score_novelty = IntegerField()
    score_presentation = IntegerField()
    score_technical = IntegerField()
    score_confidence = IntegerField()

    class Meta:
        db_table = 'reviews'
