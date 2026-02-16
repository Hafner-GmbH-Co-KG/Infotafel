from django.urls import path

from . import views

urlpatterns = [
    path("", views.anzeige, name="anzeige"),
    path("monitor/<slug:identifier>/", views.anzeige, name="monitor-anzeige"),
    path("eingabe/", views.eingabe, name="eingabe"),
    path("monitore/", views.monitorverwaltung, name="monitor-verwaltung"),
    path("api/monitor/", views.monitor_state_api, name="monitor-state-default"),
    path("api/monitor/<slug:identifier>/", views.monitor_state_api, name="monitor-state"),
]
