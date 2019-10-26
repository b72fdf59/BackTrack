from django.contrib.auth.models import User, Group
from .models import PBI, Project, ProductBacklog
from rest_framework import viewsets, generics
from .serializers import UserSerializer, GroupSerializer, PBISerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse


def getPBIfromProj(pk, all, post):
    data = []
    for id in ProductBacklog.objects.filter(
            project_id=get_object_or_404(Project, pk=pk)).values_list('PBI_id'):
        obj = PBI.objects.get(pk=id[0])
        # If post is true then do not count objects which 0 priority(which are finished), this is for when creating a new PBI
        if post and obj.priority == 0:
            continue
        else:
            data.append(obj)
    return data


class HomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/home.html'

    def get(self, request, pk):
        return Response()


class LoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/login.html'

    def get(self, request, pk):
        return Response()


class ProductBacklogView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/pb.html'

    def get(self, request, pk):
        import math
        data = getPBIfromProj(pk, True, False)
        data = sorted(data, key=lambda x: (x.priority if x.priority != 0 else math.inf, x.summary))
        sum_effort_hours, sum_story_points = 0, 0
        for PBIObj in data:
            sum_effort_hours += PBIObj.effort_hours
            sum_story_points += PBIObj.story_points
            PBIObj.sum_effort_hours = sum_effort_hours
            PBIObj.sum_story_points = sum_story_points
        context = {'data': data}
        return Response(context)


class PBIAddEditView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, pk):
        return Response({}, template_name="backtrack/addPBI.html")

    def post(self, request, pk):
        data = request.data
        PBIdata = getPBIfromProj(pk, False, True)
        priority = sorted(PBIdata, key=lambda x: (
            x.priority), reverse=True)[0].priority + 1
        pbi = PBI(summary=data['summary'], effort_hours=data['effort-hours'],
                  story_points=data['story-points'], priority=priority)
        pbi.save()
        ProductBacklog.objects.create(PBI_id=pbi.id, project_id=pk)
        return redirect(reverse('pb', kwargs={'pk': pk}))


class PBIDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/PBIdetail.html'

    def get(self, request, pk, pbipk):
        pbi = get_object_or_404(PBI, pk=pbipk)
        print(request.data)
        return Response({"PBI": pbi})

    def post(self, request, pk, pbipk):
        data = request.data
        pbi = PBI.objects.get(pk=pbipk)

        PBIList = getPBIfromProj(pk, False, True)
        remove = []
        if int(data['priority']) < pbi.priority:
            # Remove all PBI with priority higher than post data priority
            # and lesser  or equal than current PBI priority
            for PBIObj in PBIList:
                if PBIObj.priority < int(data['priority']) or PBIObj.priority >= pbi.priority:
                    remove.append(PBIObj.priority)
            PBIList = [PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Increase each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority = PBIObj.priority + 1
                PBIObj.save()
        else:
            # Remove all PBI with priority higher than post PBI priority
            # and lesser than and equal to Post data priority
            for PBIObj in PBIList:
                if PBIObj.priority <= pbi.priority or PBIObj.priority > int(data['priority']):
                    remove.append(PBIObj.priority)
            PBIList = [PBIObj for PBIObj in PBIList if PBIObj.priority not in remove]
            # Decrease each objects priority by one
            for PBIObj in PBIList:
                PBIObj.priority = PBIObj.priority - 1
                PBIObj.save()

        # Update values and save the instance
        pbi.priority = data['priority']
        pbi.summary = data['summary']
        pbi.story_points = data['story-points']
        pbi.effort_hours = data['effort-hours']
        pbi.save()

        # Redirect to product backlog
        return redirect(reverse('pb', kwargs={'pk': pk}))


class PBIDeleteView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, pk, pbipk):
        pbi = get_object_or_404(PBI, pk=pbipk)
        pbi.delete()
        return redirect(reverse('pb', kwargs={'pk': pk}))


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


# class PBIViewSet(viewsets.ModelViewSet):
#     queryset = PBI.objects.all()
#     serializer_class = PBISerializer
