from django.urls import path
from . import views

urlpatterns = [
    path('', views.anzeige, name='anzeige'),
    path('eingabe/', views.eingabe, name='eingabe'),
]
