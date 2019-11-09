from ..models import Sprint, Project, PBI, Task
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from ..helpers import addContext
from django.views.generic import CreateView, View, TemplateView


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


class AddTaskToInProgress(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = '/accounts/login'
    success_message = "PBI was added"

    def post(self, request, *args, **kwargs):
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
