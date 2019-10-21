from django.contrib.auth.models import User, Group
from backtrack.models import PBI
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, PBISerializer
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'backtrack/home.html')


def pb(request):
    return render(request, 'backtrack/pb.html')



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

<<<<<<< HEAD
=======
class PBIViewSet(viewsets.ModelViewSet):
    queryset = PBI.objects.all()
    serializer_class = PBISerializer
>>>>>>> poorva
