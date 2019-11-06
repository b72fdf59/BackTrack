from ..models import PBI, Project
# from . import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from ..helpers import addContext


def getPBIfromProj(pk, all):
    from ..models import PBI
    data, pbiList = [], PBI.objects.filter(project_id=pk)
    for pbi in pbiList:
        obj = PBI.objects.get(pk=pbi.id)
        # If all is true then do not count objects with status done(which are finished), this is for when creating a new PBI
        if obj.status == "D" and (not bool(int(all))):
            continue
        else:
            data.append(obj)
    return data


class HomeView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    redirect_field_name = '/home'
    template_name = 'backtrack/home.html'

    def get_redirect_field_name(self):
        return reverse('home')

    def get_context_data(self, **kwargs):

        if self.request.user.projectParticipant.all().exists():
            context = {}
            context = addContext(self, context)
        else:
            context = {}
        return context


class ProductBacklogView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login'
    redirect_field_name = '/home'
    template_name = 'backtrack/pb.html'

    def get_context_data(self, **kwargs):
        import math
        # query = request.query_params
        data = getPBIfromProj(
            kwargs['pk'], self.request.GET['all'] if 'all' in self.request.GET else '0')
        data = sorted(data, key=lambda x: (
            x.priority if x.status != "D" else math.inf, x.summary))
        sum_effort_hours, sum_story_points = 0, 0
        for PBIObj in data:
            sum_effort_hours += PBIObj.effort_hours
            sum_story_points += PBIObj.story_points
            PBIObj.sum_effort_hours = sum_effort_hours
            PBIObj.sum_story_points = sum_story_points
        context = {'data': data}
        context = addContext(self, context)
        return context


class AddPBI(LoginRequiredMixin, CreateView):
    model = PBI
    fields = ['summary', 'story_points', 'effort_hours']
    login_url = '/accounts/login'
    redirect_field_name = '/home'
    template_name = "backtrack/addPBI.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = addContext(self, context)
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.object.project.id}))

    def form_valid(self, form):
        PBIData = getPBIfromProj(self.kwargs['pk'], '0')
        # Initialise Priority
        priority = 0
        # Sort According to Priority
        PBIData = sorted(PBIData, key=lambda x: (
            x.priority), reverse=True)
        # If no Item in list make priority 1
        if PBIData:
            priority = PBIData[0].priority + 1
        else:
            priority = 1
        form.instance.priority = priority
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['pk'])
        return super().form_valid(form)


class updatePBI(LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'pbipk'
    kwargs = {'pk_url_kwarg': 'pbipk'}
    model = PBI
    fields = ['priority', 'summary', 'story_points', 'effort_hours']
    login_url = '/accounts/login'
    redirect_field_name = '/home'
    template_name = 'backtrack/PBIdetail.html'
    template_name_suffix = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PBI'] = self.object
        context = addContext(self, context)
        return context

    def get_success_url(self):
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.kwargs['pk']}))

    def form_valid(self, form):
        updatePBI = self.model.objects.get(pk=self.kwargs['pbipk'])
        PBIList = getPBIfromProj(self.kwargs['pk'], '0')
        remove = []
        priorityData = form.cleaned_data['priority']
        if int(priorityData) < updatePBI.priority:
            # Remove all PBI with priority higher than post data priority
            # and lesser  or equal than current PBI priority
            for PBIObj in PBIList:
                if PBIObj.priority < int(priorityData) or PBIObj.priority >= updatePBI.priority:
                    remove.append(PBIObj.priority)
            PBIList = [
                PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Increase each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority += 1
                PBIObj.save()
        else:
            # Remove all PBI with priority higher than post PBI priority
            # and lesser than and equal to Post data priority
            for PBIObj in PBIList:
                if PBIObj.priority <= updatePBI.priority or PBIObj.priority > int(priorityData):
                    remove.append(PBIObj.priority)
            PBIList = [
                PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Decrease each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority -= 1
                PBIObj.save()

        return super().form_valid(form)


class DeletePBI(LoginRequiredMixin, DeleteView):
    template_name = 'backtrack/pbi_confirm_delete.html'
    model = PBI
    login_url = '/accounts/login'
    redirect_field_name = '/home'
    pk_url_kwarg = 'pbipk'

    def get_success_url(self):
        return "{}?all=0".format(reverse('pb', kwargs={'pk': self.object.project.id}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PBI'] = self.object
        context = addContext(self, context)
        return context
