from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Client, Mission, Journal, Facture, Prestation, Ligne, Collaborateur, FeuilleDeTemps, LigneDeFeuilleDeTemps, Paiement
from .forms import LoginForm, ClientForm, MissionForm, FactureForm, PrestationForm,JournalForm, LigneForm, RechercheMissionForm, CollaborateurForm,FeuilleDeTempsForm,LigneFeuilleDeTempsForm, PaiementForm
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Sum,  Q, F
from .decorators import login_required, comptable_required, raf_required, associe_required
from django.contrib import messages
import logging
#from django.contrib.auth.hashers import check_password

# Create your views here.
# à supprimer
def index(request):
    return HttpResponse('<H1> hello all</h1>')



logger = logging.getLogger(__name__)



def login_view(request):
    """
    Vue pour gérer la connexion des utilisateurs
    """
    # Si l'utilisateur est déjà connecté, le rediriger vers la page d'accueil
    if 'collaborateur_id' in request.session:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            logger.info(f"Tentative de connexion avec email: {email}")
            
            try:
                collaborateur = Collaborateur.objects.get(email=email)
                logger.info(f"Email trouvé en base: {email}")
                
                if collaborateur.check_password(password):
                    logger.info(f"Authentification réussie pour: {email}")
                    # Stocker l'ID du collaborateur dans la session
                    request.session['collaborateur_id'] = collaborateur.id
                    
                    # Stocker le rôle pour faciliter les contrôles d'accès
                    request.session['collaborateur_role'] = collaborateur.role
                    
                    # Optionnel : définir une date d'expiration pour la session
                    request.session.set_expiry(86400)  # 24 heures
                    
                    return redirect('home')
                else:
                    logger.warning(f"Mot de passe incorrect pour: {email}")
                    form.add_error('password', 'Mot de passe incorrect')
            except Collaborateur.DoesNotExist:
                logger.warning(f"Email non trouvé en base: {email}")
                form.add_error('email', 'Email non trouvé')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """
    Vue pour gérer la déconnexion des utilisateurs
    """
    # Supprimer toutes les variables de session
    request.session.flush()
    logger.info("Utilisateur déconnecté")
    return redirect('login')

def access_denied(request):
    """
    Vue pour afficher un message d'accès refusé
    """
    return render(request, 'registration/access_denied.html')
@login_required
def home(request):
    missions_actives = Mission.objects.filter(statut='en cours').count()
    factures_en_attente = Facture.objects.filter(montant_total__gt=0).count()
    total_clients = Client.objects.count()
    total_journaux = Journal.objects.count()
    context = {
        'missions_actives': missions_actives,
        'factures_en_attente': factures_en_attente,
        'total_clients': total_clients,
        'total_journaux': total_journaux,
    }
    return render(request, 'projManagement/home.html', context)
@login_required
def clients(request):
    query = request.GET.get('q', '')
    clients_list = Client.objects.all()

    if query:
        clients_list = clients_list.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query)
        )

    return render(request, "projManagement/clients.html", {"clients": clients_list, "query": query})
@login_required
def creer_client(request):
    if request.method == 'POST':
        print("FILES:", request.FILES)  # Affiche les fichiers téléchargés
        formulaire = ClientForm(request.POST, request.FILES)
        if formulaire.is_valid():
            client = formulaire.save()
            print("Client créé:", client.id)
            print("Logo URL:", client.logo.url if client.logo else "Pas de logo")
            return HttpResponseRedirect(reverse('clients'))
        else:
            print("Erreurs du formulaire:", formulaire.errors)
    else:
        formulaire = ClientForm()
    return render(request, 'projManagement/creationClient.html', {'form': formulaire})
@login_required
def supprimer_client(request, id):
    client = Client.objects.filter(id=id).first()
    
    missionsDuClient = Mission.objects.filter(client=client)
    if missionsDuClient.exists():
        return HttpResponseRedirect(reverse('clients'))
    client.delete()
    return HttpResponseRedirect(reverse('clients'))
@login_required
def supprimer_mission(request, id):
    mission = Mission.objects.filter(id=id).first()
    
    journauxDeMission = Journal.objects.filter(mission=mission)
    if journauxDeMission.exists():
        return HttpResponseRedirect(reverse('missions'))
    mission.delete()
    return HttpResponseRedirect(reverse('missions'))
@comptable_required
def supprimer_journal(request, id):
    journal = Journal.objects.filter(id=id).first()
    facturesDuJournal = Facture.objects.filter(journal=journal)
    lignesDuJournal = Ligne.objects.filter(journal=journal)
    if facturesDuJournal.exists() or lignesDuJournal.exists():
        return HttpResponseRedirect(reverse('journaux'))
    journal.delete()
    return HttpResponseRedirect(reverse('journaux'))
@raf_required    
def supprimer_facture(request, id):
    facture = Facture.objects.filter(id=id).first()
    # j'ai abandonné l'idée de faire un modèle Paiement
    # donc il est possible de supprimer une facture sans contrainte
    # sinon il aurait fallu tenir compte du paiement
    facture.delete()
    return HttpResponseRedirect(reverse('factures'))
@comptable_required
def supprimer_ligne(request, id):
    ligne = Ligne.objects.filter(id=id).first()
    journal = ligne.journal
    # aucune contrainte de suppression sur les lignes
    # on aurait pu imaginer que si un journal est validé qu'il n'est pas possible de le supprimer
    # ni de supprimer ses lignes
    ligne.delete()
    return render(request, 'projManagement/detailJournal.html', {'journal':journal})
@login_required
def supprimer_ligne_de_feuille_de_temps(request, id):
    ligneFDT = LigneDeFeuilleDeTemps.objects.filter(id=id).first()
    feuille = ligneFDT.feuille_de_temps
    ligneFDT.delete()
    return render(request, 'projManagement/detailFeuilleDeTemps.html', {'feuille':feuille})
@login_required    
def supprimer_feuille_de_temps(request, id):
    feuille = FeuilleDeTemps.objects.filter(id=id).first()
    
    lignesDeFeuille = LigneDeFeuilleDeTemps.objects.filter(feuille_de_temps=feuille)
    if lignesDeFeuille.exists():
        return HttpResponseRedirect(reverse('feuillesDeTemps'))
    lignesDeFeuille.delete()
    return HttpResponseRedirect(reverse('feuillesDeTemps'))
@login_required
def detail_client(request, id):
    client = Client.objects.filter(id=id).first()
    return render(request, 'projManagement/detailClient.html', {'client': client})
@login_required
def modifier_client(request, id):
    client = Client.objects.filter(id=id).first()
    if request.method == 'POST':
        formulaire = ClientForm(request.POST, instance=client)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('detail_client', args=[id]))
    else:
        formulaire = ClientForm(instance=client)
    return render(request, 'projManagement/modifierClient.html', {'form': formulaire, 'client': client})





@login_required
def missions(request):
    query = request.GET.get('q', '')
    missions_list = Mission.objects.all()

    if query:
        missions_list = missions_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query) |
            Q(budget__icontains=query)
        )

    for mission in missions_list:
        # Calcul du montant facturé (existant)
        montant_facture = (
            Facture.objects.filter(journal__mission=mission)
            .aggregate(total=Sum("montant_total"))
            ["total"]
        ) or 0
        mission.montant_facture = montant_facture
        
        # Calcul du coût total des prestations (nouveau)
        cout_prestations = (
            Ligne.objects.filter(journal__mission=mission)
            .annotate(cout=F('quantite') * F('prestation__prix'))
            .aggregate(total=Sum('cout'))
            ['total']
        ) or 0
        mission.cout_prestations = cout_prestations

    return render(request, "projManagement/missions.html", {"missions": missions_list, "query": query})
@login_required
def missions_en_cours(request):
    query = request.GET.get('q', '')
    missions_list = Mission.objects.all()
    missions_list=missions_list.filter(statut="En cours")
    if query:
        missions_list = missions_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query) |
            Q(budget__icontains=query)
        )
    for mission in missions_list:
        montant_facture = (
            Facture.objects.filter(journal__mission=mission)
            .aggregate(total=Sum("montant_total"))
            ["total"]
        ) or 0
        mission.montant_facture = montant_facture
    
    
    
    
    
    
    return render(request, "projManagement/missions.html", {"missions": missions_list, "query": query})
@login_required
def missions_en_attente(request):
    query = request.GET.get('q', '')
    missions_list = Mission.objects.all()
    missions_list=missions_list.filter(statut="en attente")
    if query:
        missions_list = missions_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query) |
            Q(budget__icontains=query)
        )
    for mission in missions_list:
        montant_facture = (
            Facture.objects.filter(journal__mission=mission)
            .aggregate(total=Sum("montant_total"))
            ["total"]
        ) or 0
        mission.montant_facture = montant_facture
    
    
    
    
    
    
    return render(request, "projManagement/missions.html", {"missions": missions_list, "query": query})
@login_required
def missions_fermees(request):
    query = request.GET.get('q', '')
    missions_list = Mission.objects.all()
    
    missions_list=missions_list.filter(statut="fermé")
    if query:
        missions_list = missions_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(client__prenom__icontains=query) |
            Q(budget__icontains=query)
        )
    for mission in missions_list:
        montant_facture = (
            Facture.objects.filter(journal__mission=mission)
            .aggregate(total=Sum("montant_total"))
            ["total"]
        ) or 0
        mission.montant_facture = montant_facture
    
    
    
    
    
    return render(request, "projManagement/missions.html", {"missions": missions_list, "query": query})
@login_required
def creer_mission(request):
    if request.method == 'POST':
        formulaire = MissionForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('missions'))
    else:
        formulaire = MissionForm()
    return render(request, 'projManagement/creationMission.html', {'form': formulaire})
@login_required
def detail_mission(request, id):
    mission = Mission.objects.filter(id=id).first()
    # Calcul du montant facturé
    montant_facture = (
        Facture.objects.filter(journal__mission=mission)
        .aggregate(total=Sum("montant_total"))
        ["total"]
    ) or 0
    
    # Calcul du coût des prestations
    cout_prestations = (
        Ligne.objects.filter(journal__mission=mission)
        .annotate(cout=F('quantite') * F('prestation__prix'))
        .aggregate(total=Sum('cout'))
        ['total']
    ) or 0
    
    context = {
        'mission': mission,
        'montant_facture': montant_facture,
        'cout_prestations': cout_prestations
    }
    return render(request, 'projManagement/detailMission.html', {'mission': mission})




@login_required
def modifier_mission(request, id):
    mission = Mission.objects.filter(id=id).first()
    if request.method == 'POST':
        formulaire = MissionForm(request.POST, instance=mission)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('detail_mission', args=[id]))
    else:
        formulaire = MissionForm(instance=mission)
    return render(request, 'projManagement/modifierMission.html', {'form': formulaire, 'mission': mission})

@login_required
def reporting_mission(request):
    if request.method == 'POST':
        form = RechercheMissionForm(request.POST)
        if form.is_valid():
            # On démarre avec toutes les missions
            missions = Mission.objects.all()

            # Filtrer sur la date de début : conserver les missions dont la date de début
            # est postérieure ou égale à la valeur saisie
            date_debut = form.cleaned_data.get('date_debut')
            if date_debut:
                missions = missions.filter(start_date__gte=date_debut)

            # Filtrer sur la date de fin : conserver les missions dont la date de fin
            # est antérieure ou égale à la valeur saisie
            date_fin = form.cleaned_data.get('date_fin')
            if date_fin:
                missions = missions.filter(end_date__lte=date_fin)

            # Filtrer sur le budget minimal
            budget_min = form.cleaned_data.get('budget_min')
            if budget_min is not None:
                missions = missions.filter(budget__gte=budget_min)

            # Filtrer sur le budget maximal
            budget_max = form.cleaned_data.get('budget_max')
            if budget_max is not None:
                missions = missions.filter(budget__lte=budget_max)

            # Filtrer sur le statut (recherche insensible à la casse)
            statut_mission = form.cleaned_data.get('statut_mission')
            if statut_mission:
                missions = missions.filter(statut__icontains=statut_mission)
            
            
            for mission in missions:
                # Calcul du montant facturé (existant)
                montant_facture = (
                    Facture.objects.filter(journal__mission=mission)
                    .aggregate(total=Sum("montant_total"))
                    ["total"]
                ) or 0
                mission.montant_facture = montant_facture
                
                # Calcul du coût total des prestations (nouveau)
                cout_prestations = (
                    Ligne.objects.filter(journal__mission=mission)
                    .annotate(cout=F('quantite') * F('prestation__prix'))
                    .aggregate(total=Sum('cout'))
                    ['total']
                ) or 0
                mission.cout_prestations = cout_prestations
                
                
            
            
                
            return render(request, 'projManagement/reportingMissionResultat.html', {
                'missions': missions,
                'form': form,
                
            })
    else:
        form = RechercheMissionForm()
    return render(request, 'projManagement/reportingMission.html', {'form': form})
@comptable_required
def journaux(request):
    query = request.GET.get('q', '')
    journaux_list = Journal.objects.all()

    if query:
        journaux_list = journaux_list.filter(
            Q(mission__title__icontains=query) |
            Q(statut__icontains=query) |
            Q(date_creation__icontains=query)
        )

    return render(request, 'projManagement/journaux.html', {'journaux': journaux_list, 'query': query})




@comptable_required
def creer_journal(request):
    if request.method == 'POST':
        formulaire = JournalForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('journaux'))
    else:
        formulaire = JournalForm()
    return render(request, 'projManagement/creationJournal.html', {'form': formulaire})
@comptable_required
def detail_journal(request, id):
    journal = Journal.objects.filter(id=id).first()
    
    modifiable = not (hasattr(journal, 'facture') and journal.facture)
    return render(request, 'projManagement/detailJournal.html', {'journal': journal, 'modifiable': modifiable})


@comptable_required
def modifier_journal(request, id):
    journal = Journal.objects.filter(id=id).first()

    if hasattr(journal, 'facture') and journal.facture is not None:
        return HttpResponseRedirect(reverse('detail_journal', args=[id]))
    
    if request.method == 'POST':
        formulaire = JournalForm(request.POST, instance=journal)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('detail_journal', args=[id]))
    else:
        formulaire = JournalForm(instance=journal)
    return render(request, 'projManagement/modifierJournal.html', {'form': formulaire, 'journal': journal})


@comptable_required
def factures(request):
    query = request.GET.get('q','')
    factures_list = Facture.objects.all()
    
    
    if query :
        factures_list = factures_list.filter(
            Q(id__icontains=query) |
            Q(date_emission__icontains=query) |
            Q(montant_total__icontains=query) |
            Q(journal__mission__title__icontains=query)
            )
        
        
    return render(request, 'projManagement/factures.html', {'factures': factures_list, 'query' : query})
@raf_required
def creer_facture(request):
    if request.method == 'POST':
        formulaire = FactureForm(request.POST)
        if formulaire.is_valid():
            facture = formulaire.save(commit=False)
            
            # Calcul du montant total basé sur les lignes du journal
            journal = facture.journal
            montant_total = sum(ligne.prestation.prix * ligne.quantite for ligne in journal.lignes.all())
            
            facture.montant_total = montant_total
            facture.save()
            
            return HttpResponseRedirect(reverse('factures'))
    else:
        #formulaire = FactureForm(initial={'date_emission': now()})
        # Filtrer les journaux qui n'ont pas encore de facture associée
        journaux_disponibles = Journal.objects.filter(facture__isnull=True)
        formulaire = FactureForm(initial={'date_emission': now()})
        formulaire.fields['journal'].queryset = journaux_disponibles
    
    return render(request, 'projManagement/creationFacture.html', {'form': formulaire})
@comptable_required
def detail_facture(request, id):
    facture = Facture.objects.filter(id=id).first()
    return render(request, 'projManagement/detailFacture.html', {'facture': facture})

@comptable_required
def detail_ligne(request, id):
    # Récupère la ligne ou retourne une 404 si non trouvée
    ligne = Ligne.objects.filter(id=id).first()
    return render(request, 'projManagement/detailLigne.html', {'ligne': ligne})
@comptable_required
def modifier_ligne(request, id):
    ligne = Ligne.objects.filter(id=id).first()
    if request.method == 'POST':
        formulaire = LigneForm(request.POST, instance=ligne)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('detail_ligne', args=[id]))
    else:
        formulaire = LigneForm(instance=ligne)
    return render(request, 'projManagement/modifierLigne.html', {'form': formulaire, 'ligne': ligne})
@comptable_required
def ajouter_ligne(request, id):
    journal = Journal.objects.filter(id=id).first()
    if not journal:
        return HttpResponseRedirect(reverse('journaux'))
    
    if request.method == 'POST':
        formulaire = LigneForm(request.POST)
        if formulaire.is_valid():
            ligne = formulaire.save(commit=False)
            ligne.journal = journal
            ligne.save()
            return HttpResponseRedirect(reverse('detail_journal', args=[id]))
    else:
        formulaire = LigneForm()
        #formulaire.fields['journal'].widget = forms.HiddenInput()
    
    return render(request, 'projManagement/ajouterLigne.html', {'form': formulaire, 'journal': journal})
@login_required
def prestations(request):
    query = request.GET.get('q','')
    prestations_list = Prestation.objects.all()
    
    if query : 
        prestations_list = prestations_list.filter(
            Q(id__icontains=query) |
            Q(diminutif__icontains=query) |
            Q(description__icontains=query) |
            Q(prix__icontains=query) 
            )
        
    return render(request, 'projManagement/prestations.html', {'prestations': prestations_list, 'query' : query})
@login_required
def detail_prestation(request, id):
    prestation = Prestation.objects.filter(id=id).first()
    return render(request, 'projManagement/detailPrestation.html', {'prestation': prestation})
@raf_required
def creer_prestation(request):
    if request.method == 'POST':
        formulaire = PrestationForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('prestations'))
    else:
        formulaire = PrestationForm()
    return render(request, 'projManagement/creationPrestation.html', {'form': formulaire})
@raf_required
def modifier_prestation(request, id):
    prestation = Prestation.objects.filter(id=id).first()
    if request.method == 'POST':
        formulaire = PrestationForm(request.POST, instance=prestation)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('detail_prestation', args=[id]))
    else:
        formulaire = PrestationForm(instance=prestation)
    return render(request, 'projManagement/modifierPrestation.html', {'form': formulaire, 'prestation': prestation})
@login_required
def collaborateurs(request):
    query = request.GET.get('q', '')  # Récupère la requête de recherche
    collaborateurs_list = Collaborateur.objects.all()

    # Filtre les collaborateurs en fonction de la recherche
    if query:
        collaborateurs_list = collaborateurs_list.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'projManagement/collaborateurs.html', {'collaborateurs': collaborateurs_list, 'query': query})

@raf_required
def creer_collaborateur(request):
    if request.method == 'POST':
        formulaire = CollaborateurForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('collaborateurs'))
    else:
        formulaire = CollaborateurForm()
    return render(request, 'projManagement/creationCollaborateur.html', {'form': formulaire})
@raf_required
def supprimer_collaborateur(request, id):
    collaborateur = Collaborateur.objects.filter(id=id).first()
    feuillesDuCollaborateur = FeuilleDeTemps.objects.filter(collaborateur=collaborateur)
    
    if feuillesDuCollaborateur.exists():
        return HttpResponseRedirect(reverse('collaborateurs'))
    
    collaborateur.delete()
    return HttpResponseRedirect(reverse('collaborateurs'))
@login_required
def detail_collaborateur(request, id):
    
    collaborateur = Collaborateur.objects.filter(id=id).first()  
    return render(request, 'projManagement/detailCollaborateur.html', {'collaborateur': collaborateur})



    #journal = Journal.objects.filter(id=id).first()
    
    #modifiable = not (hasattr(journal, 'facture') and journal.facture)
    #return render(request, 'projManagement/detailJournal.html', {'journal': journal, 'modifiable': modifiable})

@raf_required
def modifier_collaborateur(request, id):
  
    collaborateur = Collaborateur.objects.filter(id=id).first()  

    if request.method == 'POST':
        formulaire = CollaborateurForm(request.POST, instance=collaborateur)
        if formulaire.is_valid():
            formulaire.save()  # Sauvegarde les modifications
            return HttpResponseRedirect(reverse('detail_collaborateur', args=[id])) 
    else:
        formulaire = CollaborateurForm(instance=collaborateur)

    return render(request, 'projManagement/modifierCollaborateur.html', {'form': formulaire, 'collaborateur': collaborateur})
@login_required
def feuilles_de_temps(request):
    
    query = request.GET.get('q', '')  # Récupère la requête de recherche
    feuilles_list = FeuilleDeTemps.objects.all()

    # Filtre les feuilles de temps en fonction de la recherche
    if query:
        feuilles_list = feuilles_list.filter(
            Q(collaborateur__nom__icontains=query) |
            Q(collaborateur__prenom__icontains=query) |
            Q(mission__title__icontains=query)
        )

    return render(request, 'projManagement/feuillesDeTemps.html', {'feuilles': feuilles_list, 'query': query})
@login_required
def detail_feuille_de_temps(request, id):
    feuille = FeuilleDeTemps.objects.filter(id=id).first()
    return render (request,'projManagement/detailFeuilleDeTemps.html', {'feuille' : feuille})
@login_required
def creer_feuille_de_temps(request):
    """
    Vue pour créer une nouvelle feuille de temps.
    """
    if request.method == 'POST':
        formulaire = FeuilleDeTempsForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('feuilles_de_temps'))  # Redirige vers la liste des feuilles de temps
    else:
        formulaire = FeuilleDeTempsForm()

    return render(request, 'projManagement/creationFeuilleDeTemps.html', {'form': formulaire})
@login_required
def ajouter_ligne_feuille_de_temps(request, id):
    feuille = FeuilleDeTemps.objects.filter(id=id).first()
    
    if request.method == 'POST':
        formulaire = LigneFeuilleDeTempsForm(request.POST)
        if formulaire.is_valid():
            ligneFDT = formulaire.save(commit=False)
            
            # Calculer le montant basé sur les heures travaillées et le tarif horaire
            montant = ligneFDT.heures_travaillees * feuille.collaborateur.tarif_horaire
            
            # Associer le montant à la ligne de feuille de temps
            ligneFDT.montant = montant  # Sauvegarder le montant calculé
            
            # Associer la feuille de temps au modèle LigneDeFeuilleDeTemps
            ligneFDT.feuille_de_temps = feuille
            
            # Sauvegarder la ligne de feuille de temps
            ligneFDT.save()
            
            # Rediriger l'utilisateur vers la page de détail de la feuille de temps
            return HttpResponseRedirect(reverse('detail_feuille_de_temps', args=[id]))
    else:
        # Si la méthode est GET, créer un formulaire vide
        formulaire = LigneFeuilleDeTempsForm()

    # Rendre la page avec le formulaire et la feuille de temps
    return render(request, 'projManagement/ajouterLigneFeuilleDeTemps.html', {'form': formulaire, 'feuille': feuille})
# Dans views.py

@raf_required
def ajouter_paiement(request, facture_id):
    """Ajouter un paiement à une facture."""
    facture = Facture.objects.get(id=facture_id)
    
    if request.method == 'POST':
        formulaire = PaiementForm(request.POST, facture=facture)
        if formulaire.is_valid():
            paiement = formulaire.save(commit=False)
            paiement.facture = facture
            paiement.save()
            messages.success(request, "Le paiement a été enregistré avec succès.")
            return HttpResponseRedirect(reverse('detail_facture', args=[facture_id]))
    else:
        formulaire = PaiementForm(facture=facture)
    
    return render(request, 'projManagement/creationPaiement.html', {
        'form': formulaire,
        'facture': facture
    })

@raf_required
def detail_paiement(request, id):
    """Afficher les détails d'un paiement."""
    paiement = Paiement.objects.get(id=id)
    return render(request, 'projManagement/detail_paiement.html', {'paiement': paiement})

@raf_required
def supprimer_paiement(request, id):
    """Supprimer un paiement."""
    paiement = Paiement.objects.get(id=id)
    facture_id = paiement.facture.id
    
    # On garde en mémoire la facture pour mettre à jour son statut après
    facture = paiement.facture
    
    paiement.delete()
    
    # Mise à jour du statut de la facture
    total_paiements = sum(p.montant for p in facture.paiements.all())
    if total_paiements == 0:
        facture.statut = 'impayé'
    elif total_paiements < facture.montant_total:
        facture.statut = 'partiellement payé'
    else:
        facture.statut = 'payé'
    facture.save()
    
    messages.success(request, "Le paiement a été supprimé avec succès.")
    return HttpResponseRedirect(reverse('detail_facture', args=[facture_id]))

# Mise à jour de la vue detail_facture pour inclure les paiements
@raf_required
def detail_facture(request, id):
    facture = Facture.objects.get(id=id)
    
    # Calculer le total des paiements
    total_paiements = sum(p.montant for p in facture.paiements.all())
    montant_restant = facture.montant_total - total_paiements
    
    return render(request, 'projManagement/detailFacture.html', {
        'facture': facture,
        'total_paiements': total_paiements,
        'montant_restant': montant_restant
    })