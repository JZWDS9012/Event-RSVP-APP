from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_auth
from django.contrib.auth import logout as logout_auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from .models import Event, Question, Choice, Relationship, Answer, Vote
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import EventForm, RelationshipForm, QuestionForm, ChoiceForm, AnswerForm, SignUpForm
from django.contrib.auth.models import User
from django.urls import reverse
from django import template
from django.core.mail import send_mass_mail, send_mail


def index(request):
    return render(request, 'rsvp_event/base.html')

def logout(request):
    logout_auth(request)
    return redirect('index')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('Username', '')
        password = request.POST.get('Password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login_auth(request, user)
            # Redirect to a success page.
            return redirect('rsvp_event:home')
        else:
            # Return an 'invalid login' error message.
            return HttpResponse("failed.")
    return render(request, 'rsvp_event/login.html')


def home(request):

    latest_event_list = Event.objects.filter(members=request.user)
    context = {'latest_event_list': latest_event_list}
    return render(request, 'rsvp_event/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user = authenticate(username = username, password = password)
            login_auth(request, user)
            send_mail('Notification from RSVP', 'Congratulations! You have signed up to RSVP successfully', 'zw360@duke.edu', {email,},fail_silently = False)            
            return redirect('rsvp_event:home')
    else:
        form = SignUpForm()
    return render(request, 'rsvp_event/signup.html', {'form': form})

def add_event(request):
    if request.method == 'POST':
        eventform = EventForm(data=request.POST)
        if eventform.is_valid():
            event = eventform.save()
            event.save()
            relationship = Relationship(event = event, user = request.user, role = 'Owner')
            relationship.save()
            return redirect('rsvp_event:home')
    else:
        eventform = EventForm()
    return render(request, 'rsvp_event/add_event.html', {'eventform': eventform})


def add_user(request, event_id):
    event = Event.objects.get(pk = event_id)
    if request.method == 'POST':
        relationshipform = RelationshipForm(data=request.POST)
        if relationshipform.is_valid():
            relationship = relationshipform.save(commit=False)
            old_relationship = Relationship.objects.filter(event=event, user=relationship.user)
            if old_relationship:
                for a_relationship in old_relationship:
                    a_relationship.role = relationship.role
                    a_relationship.save()
            else:
                relationship.event = event
                relationship.save()
            return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    else:
        relationshipform = relationshipForm()
    return render(request, 'rsvp_event/add_user.html', {'relationshipform': relationshipform, 'event_id': event_id})
    


def detail_event(request, event_id):
    user = request.user
    latest_list = []
    event = Event.objects.get(pk = event_id)
    role_list = Relationship.objects.filter(user = user, event= event)
    for a_role in role_list:
        role = a_role.role
    owner_relation = Relationship.objects.filter(event= event, role = 'Owner')
    vendor_relation = Relationship.objects.filter(event= event, role = 'Vendor')
    guest_relation = Relationship.objects.filter(event= event, role = 'Guest')
    owner_list = []
    vendor_list = []
    guest_list = []
    for relationship in owner_relation:
        owner_list.append(relationship.user)
    for relationship in vendor_relation:
        vendor_list.append(relationship.user)
    for relationship in guest_relation:
        guest_list.append(relationship.user)  
    if role == 'Owner':
        latest_question_list = Question.objects.filter(event = event)
        context = {'event':event, 'latest_question_list': latest_question_list, 'event_id': event_id, 'owner_list':owner_list, 'vendor_list': vendor_list, 'guest_list': guest_list}
        return render(request, 'rsvp_event/detail_owner.html', context)
    elif role == 'Vendor':
        event = Event.objects.get(pk = event_id)
        all_question_list = Question.objects.filter(vendor = request.user)
        latest_question_list = all_question_list.filter(event = event)
        context = {'event':event, 'latest_question_list': latest_question_list, 'event_id': event_id}
        return render(request, 'rsvp_event/detail_vendor.html', context)   
    else:
        latest_question_list = Question.objects.filter(event = event)
        latest_list = []
        for question in latest_question_list:
            latest_list.append(question)
            if question.q_type == 'Choice':
                choice_list = Choice.objects.filter(question=question)
                for choice in choice_list:
                    vote_rel = Vote.objects.filter(user=request.user, choice=choice, has_vote='True')
                    if vote_rel:
                        latest_list.append(choice)
            else:    
                answer_list = Answer.objects.filter(question=question).filter(user = request.user)
                for answer in answer_list:
                    latest_list.append(answer) 
                    break
        context = {'event':event, 'event_id': event_id, 'latest_list': latest_list }
        return render(request, 'rsvp_event/detail_guest.html', context)


def add_choice_question(request, event_id):
    if request.method == 'POST':
        questionform = QuestionForm(data=request.POST)
        if questionform.is_valid():
            question = questionform.save(commit=False)
            event = Event.objects.get(pk = event_id)
            question.event = event
            question.q_type = 'Choice'
            question.save()

            #send email
            user_list = User.objects.filter(event = event)
            email_list = []
            for us in user_list:
                email_list.append(us.email)
                pass
            message = ('Notification from RSVP', 'The owner added a question in your RSVP event. Please check your account!', 'zw124@duke.edu', email_list)
            send_mass_mail((message,), fail_silently = False)
            
            return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    return render(request, 'rsvp_event/add_choice_question.html', {'questionform': questionform,'event_id':event_id})


def add_answer_question(request, event_id):
    if request.method == 'POST':
        questionform = QuestionForm(data=request.POST)
        if questionform.is_valid():
            question = questionform.save(commit=False)
            event = Event.objects.get(pk = event_id)
            question.event = event
            question.q_type = 'Answer'
            question.save()
            
            #send email
            user_list = User.objects.filter(event = event)
            email_list = []
            for us in user_list:
                email_list.append(us.email)
                pass
            message = ('Notification from RSVP', 'The owner added a question in your RSVP event. Please check your account!', 'zw124@duke.edu', email_list)
            send_mass_mail((message,), fail_silently = False)
            
            return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    return render(request, 'rsvp_event/add_answer_question.html', {'questionform': questionform,'event_id':event_id})


def edit_question(request, event_id, question_id):
    event = Event.objects.get(pk = event_id)
    role_list = Relationship.objects.filter(event=event, user=request.user)
    for a_role in role_list:
        if a_role.role != 'Owner':
            return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    question = get_object_or_404(Question, pk=question_id)
    latest_choice_list = []
    if question.q_type == 'Choice':
        latest_choice_list = Choice.objects.filter(question = question)
    if request.method == "POST":
        if 'save' in request.POST:
            questionform = QuestionForm(request.POST, instance=question)
            if questionform.is_valid():
                question = questionform.save(commit=False)            
                question.event = event
                question.save()
                
                #send email
                user_list = User.objects.filter(event = event)
                email_list = []
                for us in user_list:
                    email_list.append(us.email)
                    pass
                message = ('Notification from RSVP', 'The owner edited a question in your RSVP event. Please check your account!', 'zw124@duke.edu', email_list)
                send_mass_mail((message,), fail_silently = False)
            
                return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
        else:
            question.delete()
            return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    else:
        questionform = QuestionForm(instance=question)
    return render(request, 'rsvp_event/edit_question.html', {'latest_choice_list':latest_choice_list, 'questionform': questionform, 'event_id':event_id, 'question_id':question_id, 'question':question})


def add_choice(request, event_id, question_id):
    if request.method == "POST":
        choiceform = ChoiceForm(request.POST)
        if choiceform.is_valid():
            choice = choiceform.save(commit=False)
            question = Question.objects.get(pk = question_id)
            choice.question = question

            choice.save()

            #send email
            event = Event.objects.get(pk = event_id)
            user_list = User.objects.filter(event = event)
            email_list = []
            for us in user_list:
                email_list.append(us.email)
                pass
            message = ('Notification from RSVP', 'The owner add a new choice in your RSVP event. Please check your account!', 'zw124@duke.edu', email_list)
            send_mass_mail((message,), fail_silently = False)
            return HttpResponseRedirect(reverse('rsvp_event:edit_question', args=(event_id,question_id,)))
    else:
        choiceform = ChoiceForm()
    return render(request, 'rsvp_event/add_choice.html', {'choiceform': choiceform})


def finalization(request, event_id, question_id):
    if request.method == "POST":
        question = Question.objects.get(pk = question_id)
        question.activate = False
        question.save()
        return HttpResponseRedirect(reverse('rsvp_event:detail_event', args=(event_id,)))
    return render(request, 'rsvp_event/finalization.html', {'event_id':event_id})

def edit_choice(request, event_id, question_id, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        if 'save' in request.POST:
            choiceform = ChoiceForm(request.POST, instance=choice)
            if choiceform.is_valid():
                choice = choiceform.save(commit=False)            
                choice.question = question
                choice.save()

                #send email
                event = Event.objects.get(pk = event_id)
                user_list = User.objects.filter(event = event)
                email_list = []
                for us in user_list:
                    email_list.append(us.email)
                    pass
                message = ('Notification from RSVP', 'The owner edited a choice in your RSVP event. Please check your account!', 'zw124@duke.edu', email_list)
                send_mass_mail((message,), fail_silently = False)
            
                return HttpResponseRedirect(reverse('rsvp_event:edit_question', args=(event_id,question_id,)))
        else:
            choice.delete()
            return HttpResponseRedirect(reverse('rsvp_event:edit_question', args=(event_id,question_id,)))
    else:
        choiceform = ChoiceForm(instance=choice)
    return render(request, 'rsvp_event/edit_choice.html', {'choiceform':choiceform})

def edit_answer(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    latest_question_list = Question.objects.filter(event = event)
    return render(request, 'rsvp_event/edit_answer.html', {'latest_question_list': latest_question_list})

def edit_answer_detail(request, event_id, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        if 'vote' in request.POST:
            try:
                selected_choice = question.choice_set.get(pk=request.POST['choice'])
            except (KeyError, Choice.DoesNotExist):
                # Redisplay the question voting form.
                return render(request, 'rsvp_event/edit_answer_detail.html', {
                    'question': question,
                    'error_message': "You didn't select a choice.",
                })
            else:
                old_voterel = Vote.objects.filter(choice=selected_choice, user=request.user, has_vote='True')
                if not old_voterel:
                    new_voterel = Vote(choice=selected_choice, user=request.user, has_vote='True')
                    new_voterel.save()
                    selected_choice.votes += 1
                    selected_choice.save()
                    choice_list = Choice.objects.filter(question=question)
                    for choice in choice_list:
                        if choice != selected_choice:
                            voterel = Vote.objects.filter(choice=choice, user=request.user, has_vote='True')
                            if voterel:
                                choice.votes -= 1
                                choice.save()
                                a_voterel = Vote(choice=choice, user=request.user, has_vote='False')
                                a_voterel.save()
                                voterel.delete()
                return HttpResponseRedirect(reverse('rsvp_event:edit_answer', args=(event_id,)))
        if 'save' in request.POST:
            old_answer = Answer.objects.filter(question=question, user=request.user)
            answer_text = request.POST.get('Answer', '')
            if old_answer:
                new_answer = Answer(answer_text=answer_text, user=request.user, question=question)
                old_answer.delete()
                new_answer.save()
            else:
                answer = Answer(answer_text=answer_text, question=question, user=request.user)
                answer.save()
            return HttpResponseRedirect(reverse('rsvp_event:edit_answer', args=(event_id,)))
    return render(request, 'rsvp_event/edit_answer_detail.html', {'question':question})










