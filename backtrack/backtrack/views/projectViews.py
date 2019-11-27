from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Project, ProjectParticipant
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from ..helpers import addContext
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


class CreateProject(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project
    fields = ['name']
    login_url = '/accounts/login'
    template_name = "backtrack/createProject.html"
    success_message = "Project was created"

    def get_success_url(self):
        # Redirect to invite members page
        return reverse('invite-project-members', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)

        # Create a project participant of the user as a Product Owner
        projectParticipant = ProjectParticipant(
            user=self.request.user, role="PO", project=form.instance)
        projectParticipant.save()
        return response


class InviteMember(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "backtrack/inviteMembers.html"
    login_url = '/accounts/login'

    def get_context_data(self, **kwargs):
        context = {}
        # Get all developers other than the current user
        developers = User.objects.all().exclude(
            username=self.request.user.username).filter(profile__role__exact="D")
        managers = User.objects.all().exclude(
            username=self.request.user.username).filter(profile__role__exact="M")

        for user in developers:
            if user.projectParticipant.all().exists:
                if user.projectParticipant.filter(project__complete=False).exists():
                    # If a user has a project which is not complete exclude him.
                    developers = developers.exclude(pk=user.pk)
        context['Developers'] = developers

        for user in managers:
            if user.projectParticipant.all().exists:
                if user.projectParticipant.filter(project__complete=False).exists():
                    # If a user has a project which is not complete exclude him.
                    managers = managers.exclude(pk=user.pk)

        context['Managers'] = managers
        # Add context variables for sidebar
        context = addContext(self, context)
        return context
    
    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False

# Send Email to team member


class EmailMember(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        # Get user to whom we have to send an email
        userID = self.request.GET['id']
        receivingUser = get_object_or_404(User, id=userID)
        recipient_email = receivingUser.email
        if recipient_email:
            # If the recepient mail exists
            username = self.request.user.username
            name = receivingUser.username

            if receivingUser.profile.role == "D":
                # If user is a developer
                # Build absolute URL for the invite link
                fullPath = self.request.build_absolute_uri(
                    reverse('add-project-developer', kwargs={'pk': kwargs['pk']}))

                link = "{}?id={}".format(
                    fullPath, userID)
                subject = "Invitation to join new project"
                message = "Dear {}, {} invites you to join a new project as a developer.\nClick on the link below to join the team.\n {}".format(
                    name, username, link)

            elif receivingUser.profile.role == "M":
                fullPath = self.request.build_absolute_uri(
                    reverse('add-project-manager', kwargs={'pk': kwargs['pk']}))

                link = "{}?id={}".format(
                    fullPath, userID)
                subject = "Invitation to join new project"
                message = "Dear {}, {} invites you to join a new project as a manager.\nClick on the link below to join the team.\n {}".format(
                    name, username, link)

            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [
                recipient_email], fail_silently=False)
            return HttpResponse()
        else:
            return HttpResponseForbidden("User does not have an email")
    
    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False


class AddDeveloper(LoginRequiredMixin, UserPassesTestMixin, View):
    model = ProjectParticipant
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        dev = get_object_or_404(User, pk=request.GET['id'])
        if request.user.profile.role == "D":
            if project.projectParticipant.all().filter(role="DT").count() <= 9:
                # If there are lesser than 9 project participants
                if not dev.projectParticipant.filter(project__complete=False).exists():
                    # If the developer has projects that are not complete
                    projectParticipant = self.model(
                        project=project, user=dev, role="DT")
                    projectParticipant.save()
                    messages.success(request, 'Successfully joined project')
                else:
                    messages.error("You are already a part of a projects")
            else:
                messages.error("This Project already has 9 developers")
        else:
            messages.error("Only Developers can be added with This link")
        return redirect(reverse('home'))
    
    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False


class AddManager(LoginRequiredMixin, UserPassesTestMixin, View):
    model = ProjectParticipant
    login_url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        manager = get_object_or_404(User, pk=request.GET['id'])

        if request.user.profile.role == "M":
            projectParticipant = self.model(
                project=project, user=manager, role="SM")
            projectParticipant.save()
            messages.success(request, 'Successfully joined project')
        else:
            messages.error("Only Managers can be added with This link")
        return redirect(reverse('home'))

    def test_func(self):
        # Get User
        user = self.request.user
        # Get project from the URL
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if user.projectParticipant.filter(project__complete=False).exists():
            userProject = user.projectParticipant.get(
                project__complete=False).project
            return userProject.pk == project.pk
        return False