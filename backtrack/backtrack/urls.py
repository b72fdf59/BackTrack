from django.urls import path
from django.conf.urls import url
from .views import PBIviews, projectViews, sprintViews, taskViews, homeViews
from django.shortcuts import redirect

urlpatterns = [
    # Home Path
    path('', homeViews.HomeView.as_view(), name='home'),

    # Paths for Product Backlog
    path('<int:pk>/pb/', PBIviews.ProductBacklogView.as_view(), name='pb'),
    path('<int:pk>/pb/add/', PBIviews.AddPBI.as_view(), name='add-pbi'),
    path('<int:pk>/pb/<int:pbipk>/update',
         PBIviews.updatePBI.as_view(), name='detail-pbi'),
    path('<int:pk>/pb/<int:pbipk>/delete',
         PBIviews.DeletePBI.as_view(), name='delete-pbi'),

    # Paths for Project (creation, invite members, send invite, accept invitation from team members)
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

    # Tasks path in Product Backlog
    path('<int:pk>/<int:spk>/<int:pbipk>/add-task/',
         taskViews.AddTask.as_view(), name='add-task'),

    # Sprint paths
    path('<int:pk>/<int:spk>/',
         sprintViews.SprintDetail.as_view(), name='detail-sprint'),
    path('<int:pk>/pb/add-pbi-to-sprint',
         sprintViews.AddPBIToSprint.as_view(), name='add-pbi-to-sprint'),
    path('<int:pk>/<int:spk>/<int:pbipk>/remove-task/',
         sprintViews.RemovePBIfromSprint.as_view(), name='remove-pbi-from-sprint'),
     path('<int:pk>/<int:spk>/complete',sprintViews.CompleteSprint.as_view() , name='complete-sprint'),

    # Tasks paths in Sprint Backlog
    path('<int:pk>/<int:spk>/<int:taskpk>/detail-task/',
         taskViews.DetailTask.as_view(), name='detail-task'),
    path('task/in-progress', taskViews.AddTaskToInProgress.as_view(),
         name='task-in-progress'),
    path('task/done', taskViews.AddTaskToDone.as_view(), name='task-done'),
    path('task/not-done', taskViews.AddTaskToNotDone.as_view(), name='task-not-done'),
    path('<int:pk>/<int:spk>/<int:taskpk>/detail-task/delete-task/',
         taskViews.DeleteTask.as_view(), name='delete-task')
]
