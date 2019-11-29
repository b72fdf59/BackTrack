from django.views.generic import CreateView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from ..models import Sprint, Project, PBI, Task
from ..forms import CreateSprintForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.contrib.auth.models import User
from ..helpers import addContext, getPBIfromProj
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages


class CreateSprint(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Sprint
    form_class = CreateSprintForm
    template_name = "backtrack/createSprint.html"
    login_url = '/accounts/login'
    success_message = "Sprint was created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context variables for sidebar
        context = addContext(self, context)
        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Get all sprints for a project
        sprintList = project.sprint.all()

        for sprint in sprintList:
            if sprint.available:
                # If a sprint is running redirect back
                messages.error(self.request, 'Sprint is in Progress')
                return redirect(self.request.path_info)

        form.instance.project = project
        return super().form_valid(form)

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


class SprintDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    pk_url_kwarg = 'pbipk'
    login_url = '/accounts/login'
    template_name = 'backtrack/sprintDetail.html'

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])

        # Get PBI for current sprint
        PBIList = getPBIfromProj(
            self.kwargs['pk'], '1').filter(sprint_id=sprint.id)

        # Get tasks for each PBI
        task = []
        for pbi in PBIList:
            task.append(pbi.task.all())
        context = {'data': PBIList, 'sprint': sprint, 'task': task}

        # Add context variables for sidebar
        context = addContext(self, context)

        if sprint.complete == False and sprint.remainingDays == 0 and context['ProjectParticipant'].role == "DT":
            messages.error(self.request, "Please Complete Sprint")

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


class AddPBIToSprint(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "PBI was added"

    def post(self, request, *args, **kwargs):

        import json
        from ..models import PBI
        # Do we get the correct sprint?
        # We have to do it this way cause we have a property available and not a field
        sprint = self.request.user.projectParticipant.get(
            project__complete=False).project.sprint.all().order_by('-start')[0]
        PBIid = request.POST.get('PBIs')
        if PBIid:
            # If the requqest was sent from the detail page
            addPBI = get_object_or_404(PBI, pk=PBIid)
            if addPBI.sprint and addPBI.status != "U":
                # If PBI has a sprint
                messages.error(
                    self.request, "PBI is in a another sprint")
            elif not (sprint or sprint.available):
                # If there is no current sprint or if the sprint is not available
                messages.error(
                    self.request, "No such sprint")
            elif sprint.remainingCapacity < addPBI.story_points:
                # If the remaining capacity is lesser than the story points of the PBI
                messages.error(
                    self.request, "Sprint remaining capacity is lesser than PBI capactiy")
            else:
                # Successfully added sprint
                messages.success(
                    self.request, "Successfully added PBIs to sprint")
                addPBI.addToSprint(sprint)
                addPBI.save()

            # Redirect to Product Backlog
            return redirect(reverse('pb', kwargs={'pk': self.kwargs['pk']}))
        else:
            # If an ajax request is sent from the Product Backlog
            if not (sprint or sprint.available):
                # If there is no current sprint or if the sprint is not available
                response = JsonResponse({"error": "No current Sprint"})
                response.status_code = 400
                return response

            # Read json data
            data = json.loads(request.body)
            PBIidList = data['PBIs']

            if len(PBIidList) == 0:
                # If there are no PBIs
                response = JsonResponse({"error": "Please select PBIs"})
                response.status_code = 400
                return response
            else:
                PBIList = []
                totCap = 0

                # Add each PBI sent in the request to a list
                for PBIid in PBIidList:
                    myPBI = get_object_or_404(PBI, pk=PBIid)
                    totCap += myPBI.story_points
                    PBIList.append(myPBI)

                if sprint.remainingCapacity < totCap:
                    # If the remaining capacity is lesser than the story points of all the PBI
                    response = JsonResponse(
                        {"error": "Sprint remaining capacity is lesser than all PBI capactiy"})
                    response.status_code = 400
                    return response
                else:
                    # Add all the PBI in the list to the sprint
                    for PBI in PBIList:
                        if not PBI.sprint or PBI.status == "U":
                            PBI.addToSprint(sprint)
                            PBI.save()
                            response = JsonResponse(
                                {"success": "Successfully added PBIs to sprint"})
                    return response

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


class RemovePBIfromSprint(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, TemplateView):
    # pk_url_kwarg = 'pbipk'
    model = PBI
    login_url = '/accounts/login'
    template_name = "backtrack/remove_PBI_from_Sprint.html"
    success_message = "PBI was deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context variables for sidebar
        context = addContext(self, context)
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        context['Sprint'] = sprint
        context['PBI'] = pbi
        context['Project'] = project
        return context

    def post(self, request, **kwargs):
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        pbi.task.all().delete()
        pbi.markNotDone()
        pbi.sprint = None
        pbi.save()
        return redirect(reverse('detail-sprint', kwargs={'pk': self.kwargs['pk'], 'spk': self.kwargs['spk']}))

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


class CompleteSprint(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "PBI Completed"

    def post(self, request, **kwargs):
        from datetime import date
        sprintID = kwargs['spk']
        sprint = get_object_or_404(Sprint, pk=sprintID)
        if sprint.complete == False:

            # Get PBI which are in progress and mark them unfinished
            unfinishedPBI = sprint.pbi.filter(status__exact="P")
            for PBI in unfinishedPBI:
                PBI.markUnfinished()
                PBI.save()

            sprint.end = date.today()
            sprint.complete = True
            sprint.save()
            response = JsonResponse(
                {"success": "Successfully Completed Sprint"})
        else:
            response = JsonResponse(
                {"error": "Sprint already complete"})
            response.status_code = 400
        return response

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
