from django.contrib.auth.models import User, Group
from .models import PBI, Project
from django.views import View
from django.views.generic import TemplateView
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse


def getPBIfromProj(pk, all):
    from .models import PBI
    data, pbiList = [], PBI.objects.filter(Project_id=pk)
    for pbi in pbiList:
        obj = PBI.objects.get(pk=pbi.id)
        # If all is true then do not count objects with status done(which are finished), this is for when creating a new PBI
        if obj.status == "D" and (not bool(int(all))):
            continue
        else:
            data.append(obj)
    return data


class HomeView(TemplateView):
    template_name = 'backtrack/home.html'

    def get_context_data(self, **kwargs):
        context = {}
        return context


class LoginView(TemplateView):
    template_name = 'backtrack/login.html'

    def get_context_data(self, **kwargs):
        context = {}
        return context


class ProductBacklogView(TemplateView):
    template_name = 'backtrack/pb.html'

    def get_context_data(self, **kwargs):
        import math
        # query = request.query_params
        data = getPBIfromProj(self.kwargs['pk'], self.request.GET['all'])
        data = sorted(data, key=lambda x: (
            x.priority if x.status != "D" else math.inf, x.summary))
        sum_effort_hours, sum_story_points = 0, 0
        for PBIObj in data:
            sum_effort_hours += PBIObj.effort_hours
            sum_story_points += PBIObj.story_points
            PBIObj.sum_effort_hours = sum_effort_hours
            PBIObj.sum_story_points = sum_story_points
        context = {'data': data}
        return context


class AddPBI(TemplateView):
    template_name="backtrack/addPBI.html"
    def get_context_data(self, **kwargs):
        context = {}
        return context

    def post(self, request, pk):
        data = request.POST
        PBIData = getPBIfromProj(pk, '0')

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
        pbi = PBI(summary=data['summary'], effort_hours=data['effort-hours'],
                  story_points=data['story-points'], priority=priority, Project_id=pk)
        pbi.save()
        return redirect("{}?all=0".format(reverse('pb', kwargs={'pk': pk})))


class PBIDetailEdit(TemplateView):
    template_name = 'backtrack/PBIdetail.html'

    def get_context_data(self, **kwargs):
        pbi = get_object_or_404(PBI, pk=self.kwargs['pbipk'])
        context = {"PBI": pbi}
        return context

    def post(self, request, pk, pbipk):
        data = request.POST
        pbi = PBI.objects.get(pk=pbipk)

        PBIList = getPBIfromProj(pk, '0')
        remove = []
        if int(data['priority']) < pbi.priority:
            # Remove all PBI with priority higher than post data priority
            # and lesser  or equal than current PBI priority
            for PBIObj in PBIList:
                if PBIObj.priority < int(data['priority']) or PBIObj.priority >= pbi.priority:
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
                if PBIObj.priority <= pbi.priority or PBIObj.priority > int(data['priority']):
                    remove.append(PBIObj.priority)
            PBIList = [
                PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Decrease each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority -= 1
                PBIObj.save()

        # Update values and save the instance
        pbi.priority = data['priority']
        pbi.summary = data['summary']
        pbi.story_points = data['story-points']
        pbi.effort_hours = data['effort-hours']
        pbi.save()

        # Redirect to product backlog
        return redirect("{}?all=0".format(reverse('pb', kwargs={'pk': pk})))



class DeletePBI(View):

    def post(self, request, pk, pbipk):
        pbiList = getPBIfromProj(pk, '0')

        pbiToDel = get_object_or_404(PBI, pk=pbipk)

        for pbi in pbiList:
            if pbi.priority > pbiToDel.priority:
                pbi.priority -= 1
                pbi.save()

        pbiToDel.delete()
        return redirect("{}?all=0".format(reverse('pb', kwargs={'pk': pk})))
