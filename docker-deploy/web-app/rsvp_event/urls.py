from django.urls import path

from . import views

app_name = 'rsvp_event'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('', views.logout, name='logout'),
    path('home/add_event/', views.add_event, name='add_event'),
    path('home/<int:event_id>/', views.detail_event, name='detail_event'),
    path('home/<int:event_id>/add_user/', views.add_user, name='add_user'),
    path('home/<int:event_id>/add_choice_question/', views.add_choice_question, name='add_choice_question'),
    path('home/<int:event_id>/add_answer_question/', views.add_answer_question, name='add_answer_question'),
    path('home/<int:event_id>/<int:question_id>/', views.edit_question, name='edit_question'),
    path('home/<int:event_id>/<int:question_id>/add_choice/', views.add_choice, name='add_choice'),
    path('home/<int:event_id>/<int:question_id>/finalization/', views.finalization, name='finalization'),
    path('home/<int:event_id>/<int:question_id>/<int:choice_id>/', views.edit_choice, name='edit_choice'),
    path('home/<int:event_id>/edit_answer/', views.edit_answer, name='edit_answer'),
    path('home/<int:event_id>/edit_answer/', views.edit_answer, name='edit_answer'),
    path('home/<int:event_id>/edit_answer/<int:question_id>', views.edit_answer_detail, name='edit_answer_detail'),
]
