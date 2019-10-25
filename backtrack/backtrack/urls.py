from django.urls import path, include
from django.conf.urls import url
from backtrack import views

urlpatterns = [
    path('', views.LoginView.as_view(),name = 'home'),
    path('pb/', views.ProductBacklogView.as_view(),name='pb'),
]
