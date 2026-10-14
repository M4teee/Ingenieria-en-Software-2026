from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hola),
    path('seguimiento/<str:codigo>/', views.seguimiento, name='seguimiento'),
]

