from django import forms

from .models import Event, Relationship, Question, Choice, Answer
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import UserCreationForm

class EventForm(forms.ModelForm):

	class Meta:
		model = Event
		fields = ('title','date','location',)

class RelationshipForm(forms.ModelForm):

	class Meta:
		model = Relationship
		fields = ('role','user',)

class QuestionForm(forms.ModelForm):
	#vendors = forms.ModelMultipleChoiceField(queryset=User.objects.all())
	class Meta:
		model = Question
		fields = ('question_text', 'vendor', )

class ChoiceForm(forms.ModelForm):

	class Meta:
		model = Choice
		fields = ('choice_text',)

#changed
class AnswerForm(forms.ModelForm):

	class Meta:
		model = Answer
		fields = ('answer_text',)

class SignUpForm(UserCreationForm):
	username = forms.CharField(required = True , max_length = 30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
	email = forms.EmailField(required = True, max_length=254, help_text='Required. Inform a valid email address.')
	password1 = forms.CharField(required = True, min_length=8,label='Enter password', widget=forms.PasswordInput,help_text='Required. 8 characters or more. Letters, digits and @/./+/-/_ only.')
	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', )