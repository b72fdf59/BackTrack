from django.contrib.auth.models import User, Group
from .models import PBI
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, PBISerializer
from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

class HomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/home.html'

    def get(self,request,pk):
        return Response()

class LoginnView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/login.html'

    def get(self,request,pk):
        return Response()


class ProductBacklogView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'backtrack/pb.html'

    def get(self,request,pk):
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
