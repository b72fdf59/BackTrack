from django.contrib.auth.models import User, Group
from .models import PBI, Project, ProductBacklog
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, PBISerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

def getPBIfromProj(pk,all,post):
    data =[]
    for id in ProductBacklog.objects.filter(
                project_id=get_object_or_404(Project, pk=pk)).values_list('PBI_id'):
            obj = PBI.objects.get(pk=id[0])
            print(obj.priority)
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
        data = getPBIfromProj(pk,True,False)
        sorted(data, key=lambda x: (x.priority, x.summary))
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
        PBIdata = getPBIfromProj(pk,False,True)
        pbi = PBI(summary=data['summary'],effort_hours=data['effort-hours'],story_points=data['story-points'],priority=len(PBIdata) + 1)
        pbi.save()
        ProductBacklog.objects.create(PBI_id=pbi.id,project_id=pk)
        return redirect(reverse('pb',kwargs={'pk':1}))


class PBIEditView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/editPBI.html'

    def get(self, request, pk):
        return Response({})


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
