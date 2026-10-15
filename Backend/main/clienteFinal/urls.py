from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.form, name='clienteFinal'), 
    path('seguimiento/<str:codigo>/', views.seguimiento, name='seguimiento'),
]
