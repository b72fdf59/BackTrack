from django.urls import path, include
from django.conf.urls import url
from backtrack import views
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda x: redirect('1/'),name='home'),
    path('<int:pk>/', views.HomeView.as_view(),name = 'home-project'),
    path('<int:pk>/pb/', views.ProductBacklogView.as_view(),name='pb'),
]
