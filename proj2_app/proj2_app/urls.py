from django.contrib import admin
from django.urls import path, include
from projManagement import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('guide/', views.guide_utilisation, name='guide_utilisation'),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Includes auth-related URLs
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('clients/', views.clients, name='clients'),
    path('clients/<int:id>/', views.detail_client, name='detail_client'),
    path('clients/creer/', views.creer_client, name='creer_client'),
    path('clients/<int:id>/modifier/', views.modifier_client, name='modifier_client'),
    path('clients/<int:id>/supprimer/', views.supprimer_client, name='supprimer_client'),
    path('missions/', views.missions, name='missions'),
    path('missionsEnCours/', views.missions_en_cours, name='missions_en_cours'),
    path('missionsEnAttente/', views.missions_en_attente, name='missions_en_attente'),
    path('missionsFermees/', views.missions_fermees, name='missions_fermees'),
    path('missions/creer/', views.creer_mission, name='creer_mission'),
    path('missions/<int:id>/', views.detail_mission, name='detail_mission'),
    path('missions/<int:id>/modifier/', views.modifier_mission, name='modifier_mission'),
    path('factures/', views.factures, name='factures'),
    path('factures/<int:id>/', views.detail_facture, name='detail_facture'),
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
    path('missions/reporting/', views.reporting_mission, name='reporting_mission'),
    path('collaborateurs/', views.collaborateurs, name='collaborateurs'),
    path('collaborateurs/creer/', views.creer_collaborateur, name='creer_collaborateur'),
    path('collaborateurs/<int:id>/', views.detail_collaborateur, name='detail_collaborateur'),
    path('collaborateurs/<int:id>/modifier/', views.modifier_collaborateur, name='modifier_collaborateur'),
    path('collaborateurs/<int:id>/supprimer/', views.supprimer_collaborateur, name='supprimer_collaborateur'),
    path('feuilles-de-temps/', views.feuilles_de_temps, name='feuilles_de_temps'),
    path('feuilles-de-temps/creer/', views.creer_feuille_de_temps, name='creer_feuille_de_temps'),
    path('feuiiles-de-temps/<int:id>/' ,views.detail_feuille_de_temps, name ='detail_feuille_de_temps'),
    path('feuilles-de-temps/<int:id>/ajouter_ligne_feuille_de_temps/', views.ajouter_ligne_feuille_de_temps, name='ajouter_ligne_feuille_de_temps'),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('factures/<int:facture_id>/ajouter-paiement/', views.ajouter_paiement, name='ajouter_paiement'),
    path('paiements/<int:id>/', views.detail_paiement, name='detail_paiement'),
    path('paiements/<int:id>/supprimer/', views.supprimer_paiement, name='supprimer_paiement'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)