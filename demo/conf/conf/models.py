from django.models import Model, ManyToManyField, ForeignKey, CharField, TextField, DateTimeField, IntegerField
from django.contrib.auth.models import User

class UserProfile(Model):
    user = ForeignKey(User)

class Paper(Model):
    authors = ManyToManyField(User)
    reviewers = ManyToManyField(User)

class PaperVersion(Model):
    paper = ForeignKey(paper)

    title = CharField(1024)
    contents = CharField(1024) #filename
    abstract = TextField()
    time = DateTimeField(auto_now_add=True)

class Tag(Model):
    name = CharField(32)
    paper = ForeignKey(Paper)

class Review(Model):
    time = DateTimeField(auto_now_add=True)
    paper = ForeignKey(Paper)
    reviewer = ForeignKey(User)
    comment = TextField()

    score_novelty = IntegerField()
    score_presentation = IntegerField()
    score_technical = IntegerField()
    score_confidence = IntegerField()
