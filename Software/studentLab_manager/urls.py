from django.urls import path
from .views import MangerView

urlpatterns = [
    path('ADASLAB/', MangerView.index),
]