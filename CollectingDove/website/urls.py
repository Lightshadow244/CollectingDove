from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export', views.exportValue, name='exportValue'),
    path('startTrade', views.startTrade, name='startTrade'),
    path('stopTrade', views.stopTrade, name='stopTrade'),
]
