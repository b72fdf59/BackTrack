from django.urls import path
from django.conf.urls import url
from .views import PBIviews, projectViews, sprintViews, taskViews
from django.shortcuts import redirect

urlpatterns = [
    # path('', lambda x: redirect('1/'),name='home'),
    path('', PBIviews.HomeView.as_view(), name='home'),
    path('<int:pk>/pb/', PBIviews.ProductBacklogView.as_view(), name='pb'),
    path('<int:pk>/pb/add/', PBIviews.AddPBI.as_view(), name='add-pbi'),
    path('<int:pk>/pb/<int:pbipk>/update',
         PBIviews.updatePBI.as_view(), name='detail-pbi'),
    path('<int:pk>/pb/<int:pbipk>/delete',
         PBIviews.DeletePBI.as_view(), name='delete-pbi'),
    path('project/create', projectViews.CreateProject.as_view(),
         name='create-project'),
    path('project/create/<int:pk>/inviteList', projectViews.InviteMember.as_view(),
         name='invite-project-members'),
    path('<int:pk>/inviteAccept', projectViews.EmailMember.as_view(),
         name='email-member'),
    path('project/create/<int:pk>/add/developer', projectViews.AddDeveloper.as_view(),
         name='add-project-developer'),
    path('<int:pk>/create/sprint',
         sprintViews.CreateSprint.as_view(), name='create-sprint'),
    path('<int:pk>/<int:spk>/<int:pbipk>/add-task/',
         taskViews.AddTask.as_view(), name='add-task'),
    path('<int:pk>/<int:spk>/<int:taskpk>/detail-task/',
         taskViews.UpdateTask.as_view(), name='detail-task'),
    path('<int:pk>/<int:spk>/',
         sprintViews.SprintDetail.as_view(), name='detail-sprint'),
    path('<int:pk>/pb/add-pbi-to-sprint',
         sprintViews.AddPBIToSprint.as_view(), name='add-pbi-to-sprint'),
     path('task/in-progress',taskViews.AddTaskToInProgress.as_view(), name='task-in-progress')
]
