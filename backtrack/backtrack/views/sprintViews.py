from django.views.generic import CreateView, View, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from ..models import Sprint, Project, PBI, Task
from ..forms import CreateSprintForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth.models import User
from ..helpers import addContext
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages


def getPBIfromProj(pk, all):
    from ..models import PBI
    data, pbiList = [], PBI.objects.filter(project_id=pk)
    for pbi in pbiList:
        obj = PBI.objects.get(pk=pbi.id)
        # If all is true then do not count objects with status done(which are finished), this is for when creating a new PBI
        if obj.status == 'D' and (not bool(int(all))):
            continue
        else:
            data.append(obj)
    return data

def getTaskfromProj(pk, all):
    from ..models import Task
    data, TaskList = [], Task.objects.all()
    for task in TaskList:
        obj = Task.objects.get(pk=task.id)
        data.append(obj)
    return data

class CreateSprint(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sprint
    form_class = CreateSprintForm
    template_name = "backtrack/createSprint.html"
    login_url = '/accounts/login'
    success_message = "Sprint was created"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        sprintList = project.sprint.all()
        for sprint in sprintList:
            if sprint.available:
                messages.error(self.request, 'Sprint is in Progress')
                return redirect(self.request.path_info)
        form.instance.project = project
        return super().form_valid(form)


class SprintDetail(LoginRequiredMixin, TemplateView):
    pk_url_kwarg = 'pbipk'
    login_url = '/accounts/login'
    template_name = 'backtrack/sprintDetail.html'

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        pbi = get_object_or_404(PBI, pk=self.kwargs['spk'])
        data = getPBIfromProj(self.kwargs['pk'], '0')
        task = Task.objects.all()
        PBIList = []
        for pbi in data:
            if pbi.sprint == sprint:
                PBIList.append(pbi)
        context = {'data': PBIList, 'sprint': sprint, 'task': task}
        context = addContext(self, context)
        return context

class AddTask(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    pk_url_kwarg = 'pbipk'
    model = Task
    fields = ['summary', 'effort_hours']
    login_url = '/accounts/login'
    template_name = "backtrack/addTask.html"
    success_message = "Task was created"

    def get_context_data(self, **kwargs):
        sprint = get_object_or_404(Sprint, pk=self.kwargs['spk'])
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        context['sprint'] = sprint
        context['pbi'] = pbi
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('detail-sprint', kwargs={'pk': self.object.project.id, 'spk': self.object.sprint.id}))

    def form_valid(self, form):
        form.instance.pbi = get_object_or_404(
            PBI, pk=self.kwargs['pbipk'])
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['pk'])
        form.instance.sprint = get_object_or_404(
            Sprint, pk=self.kwargs['pk'])
        return super().form_valid(form)


class AddPBIToSprint(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "PBI was added"

    def post(self, request, *args, **kwargs):

        import json
        from ..models import PBI
        # Do we get the correct sprint?
        sprint = self.request.user.projectParticipant.get(
            project__complete=False).project.sprint.all().order_by('-start')[0]
        PBIid = request.POST.get('PBIs')
        if PBIid:
            addPBI = get_object_or_404(PBI, pk=PBIid)
            if not sprint:
                messages.error(
                    self.request, "No such sprint")
            elif sprint.remainingCapacity < addPBI.story_points:
                messages.error(
                    self.request, "Sprint remaining capacity is lesser than PBI capactiy")
            else:
                messages.success(
                    self.request, "Successfully added PBIs to sprint")
                addPBI.addToSprint(sprint)
                addPBI.save()
            return redirect(reverse('pb', kwargs={'pk': self.kwargs['pk']}))
        else:
            if not sprint:
                response = JsonResponse({"error": "No current Sprint"})
                response.status_code = 400
                return response
            data = json.loads(request.body)
            PBIidList = data['PBIs']
            if len(PBIidList) == 0:
                response = JsonResponse({"error": "Please select PBIs"})
                response.status_code = 400
                return response
            else:
                if not sprint:
                    response = JsonResponse({"error": "No current Sprint"})
                    response.status_code = 400
                    return response
                PBIList = []
                totCap = 0
                for PBIid in PBIidList:
                    myPBI = get_object_or_404(PBI, pk=PBIid)
                    totCap += myPBI.story_points
                    PBIList.append(myPBI)
                if sprint.remainingCapacity < totCap:
                    response = JsonResponse(
                        {"error": "Sprint remaining capacity is lesser than all PBI capactiy"})
                    response.status_code = 400
                    return response
                else:
                    for PBI in PBIList:
                        PBI.addToSprint(sprint)
                        PBI.save()
                        response = JsonResponse(
                            {"success": "Successfully added PBIs to sprint"})
                    return response
