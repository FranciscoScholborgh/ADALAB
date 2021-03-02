from django.urls import path
from .views import StudentLabView

urlpatterns = [
    path('', StudentLabView.index),
    path('sdtconsult/', StudentLabView.sdtConsult),
    path('device_status/', StudentLabView.deviceStatus),
]