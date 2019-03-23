from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.


TYPE_CHOICES = (
    ('Choice', 'Choice'),
    ('Answer', 'Answer'),
)
    
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    event = models.ForeignKey('Event',on_delete=models.CASCADE)
    q_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    activate = models.BooleanField(default=True)
    def __str__(self):
        return self.question_text

#changed
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.answer_text

    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    members = models.ManyToManyField(User, through='Vote')
    def __str__(self):
        return self.choice_text

    
class Event(models.Model):
    title = models.CharField(max_length=255, null=True, blank=False, default='untitled')
    location = models.CharField(max_length=255, null=True, blank=False, default='undecided')
    date = models.DateField(null=True, blank=False)
    members = models.ManyToManyField(User, through='Relationship')
    def __str__(self):
        return self.title

ROLE_CHOICES = (
    ('Owner', 'Owner'),
    ('Vendor', 'Vendor'),
    ('Guest', 'Guest'),
)

class Relationship(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Vote(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_vote = models.BooleanField(default=False)


