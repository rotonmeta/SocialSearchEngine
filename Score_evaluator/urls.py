from django.urls import path
from . import views

urlpatterns = [
    path('similarity/', views.similarity, name='similarity'),
]