from django.urls import path, include
from django.conf.urls import url
from backtrack import views
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda x: redirect('1/'),name='home'),
    path('<int:pk>/', views.HomeView.as_view(),name = 'home-project'),
    path('<int:pk>/pb/', views.ProductBacklogView.as_view(),name='pb'),
    path('<int:pk>/pb/add/', views.PBIAddEditView.as_view(),name='add'),
    path('<int:pk>/pb/<int:pbipk>/', views.PBIDetailView.as_view(),name='detail'),
    path('<int:pk>/pb/<int:pbipk>/delete', views.PBIDeleteView.as_view(),name='delete'),
    # path('??',views.LoginView.as_view(),name='loginlanding'),
]
