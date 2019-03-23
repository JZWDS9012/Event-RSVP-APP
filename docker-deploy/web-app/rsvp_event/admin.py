from django.contrib import admin

# Register your models here.

from .models import Event, Relationship, Question, Answer, Choice, Vote

admin.site.register(Event)
admin.site.register(Relationship)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Choice)
admin.site.register(Vote)
