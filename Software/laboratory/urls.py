from django.urls import path
from .views import LaboratoryView

urlpatterns = [
    path('laboratory/', LaboratoryView.laboratory),
    path('preinforme/', LaboratoryView.preinforme),
]