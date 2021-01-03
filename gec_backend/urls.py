"""GEC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('getCurUserID', views.getCurUserID, name = 'getCurUserID'),
    path('createUser/', views.createUser, name = 'createUser'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
    path('getUserByID/', views.getUserByID, name = 'getUserByID'),
    path('delUserByID/', views.delUserByID, name = 'delUserByID'),
    path('changeInfo/', views.changeInfo, name = 'changeInfo'),
    path('getUserSentences/', views.getUserSentences, name = 'getUserSentences'),
    path('getSentenceByType/', views.getSentenceByType, name = 'getSentenceByType'),
    path('getTypeBySentence/', views.getTypeBySentence, name = 'getTypeBySentence'),
    path('correctSentence/', views.correctSentence, name = 'correctSentence'),
    path('deleteSentences/', views.deleteSentences, name = 'deleteSentences'),
    path('addWord/', views.addWord, name = 'addWord'),
    path('getOftenTypes/', views.getOftenTypes, name = 'getOftenTypes'),
    path('getMostUserWords/', views.getMostUserWords, name = 'getMostUserWords'),
    path('searchWord/', views.searchWord, name = 'searchWord'),
    path('getUserVocab/', views.getUserVocab, name = 'getUserVocab'),
    path('delWord/', views.delWord, name = 'delWord'),
    path('getUserNameByID/', views.getUserNameByID, name = 'getUserNameByID'),
    path('validatepwd/', views.validatepwd, name = 'validatepwd'),
    path('upLoad/', views.uploadFile, name = 'uploadFile'),
    path('showFiles/', views.showFiles, name = 'showFiles'),
    path('downloadFile/', views.downloadFile, name = 'downloadFile'),
    path('deleteFile/', views.deleteFile, name = 'deleteFile')
]