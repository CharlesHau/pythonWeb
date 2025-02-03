from django.contrib import admin
from django.urls import path, include
from projManagement import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Includes auth-related URLs
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('clients/', views.clients, name='clients'),
    path('clients/<int:id>/', views.detail_client, name='detail_client'),
    path('clients/creer/', views.creer_client, name='creer_client'),
    path('clients/<int:id>/modifier/', views.modifier_client, name='modifier_client'),
    path('missions/', views.missions, name='missions'),
    path('missions/creer/', views.creer_mission, name='creer_mission'),
    path('missions/<int:id>/', views.detail_mission, name='detail_mission'),
    path('missions/<int:id>/modifier/', views.modifier_mission, name='modifier_mission'),
    path('factures/', views.factures, name='factures'),
    path('factures/creer/', views.creer_facture, name='creer_facture'),
    path('prestations/', views.prestations, name='prestations'),
    path('prestations/creer/', views.creer_prestation, name='creer_prestation'),
    path('prestations/<int:id>/', views.detail_prestation, name='detail_prestation'),
    path('prestations/<int:id>/modifier/', views.modifier_prestation, name='modifier_prestation'),
    path('journaux/', views.journaux, name='journaux'),
    path('journaux/creer/', views.creer_journal, name='creer_journal'),
    path('journaux/<int:id>/', views.detail_journal, name='detail_journal'),
    path('journaux/<int:id>/ajouter_ligne/', views.ajouter_ligne, name='ajouter_ligne'),
    path('journaux/<int:id>/modifier/', views.modifier_journal, name='modifier_journal'),
    path('lignes/<int:id>/', views.detail_ligne, name='detail_ligne'),
    path('lignes/<int:id>/modifier/', views.modifier_ligne, name='modifier_ligne'),

]
