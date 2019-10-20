from django.urls import path, include
from django.conf.urls import url
from .views import home, pb

from . import views

urlpatterns = [
    url(r'^home/', views.home, name='home2'),
    url(r'^pb/', views.pb, name='pb'),
    url(r'^', views.home, name='home')
]
