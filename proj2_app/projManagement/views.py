from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Client, Mission, Journal, Facture, Prestation, Ligne
from .forms import ClientForm, MissionForm, FactureForm, PrestationForm,JournalForm, LigneForm, RechercheMissionForm
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Sum,  Q

# Create your views here.
# à supprimer
def index(request):
    return HttpResponse('<H1> hello all</h1>')


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
def creer_client(request):
    if request.method == 'POST':
        formulaire = ClientForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('clients'))
    else:
        formulaire = ClientForm()
    return render(request, 'projManagement/creationClient.html', {'form': formulaire})

def detail_client(request, id):
    client = Client.objects.filter(id=id).first()
    return render(request, 'projManagement/detailClient.html', {'client': client})

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


def supprimer_client(request,id):
    client = Client.objects.filter(id=id).first()
    missionsDuClient = Mission.objects.filter(client=client)
    
    if missionsDuClient.exists():
        return render(request, 'projManagement/detailClient.html', {'client': client})
    client.delete()
    clients(request)



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
        montant_facture = (
            Facture.objects.filter(journal__mission=mission)
            .aggregate(total=Sum("montant_total"))
            ["total"]
        ) or 0
        mission.montant_facture = montant_facture

    return render(request, "projManagement/missions.html", {"missions": missions_list, "query": query})



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

def creer_mission(request):
    if request.method == 'POST':
        formulaire = MissionForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('missions'))
    else:
        formulaire = MissionForm()
    return render(request, 'projManagement/creationMission.html', {'form': formulaire})
def detail_mission(request, id):
    mission = Mission.objects.filter(id=id).first()
    return render(request, 'projManagement/detailMission.html', {'mission': mission})





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
                montant_facture = (
                    Facture.objects.filter(journal__mission=mission)
                    .aggregate(total=Sum("montant_total"))
                    ["total"]
                ) or 0
                mission.montant_facture = montant_facture
                
            return render(request, 'projManagement/reportingMissionResultat.html', {
                'missions': missions,
                'form': form,
            })
    else:
        form = RechercheMissionForm()
    return render(request, 'projManagement/reportingMission.html', {'form': form})

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





def creer_journal(request):
    if request.method == 'POST':
        formulaire = JournalForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('journaux'))
    else:
        formulaire = JournalForm()
    return render(request, 'projManagement/creationJournal.html', {'form': formulaire})

def detail_journal(request, id):
    journal = Journal.objects.filter(id=id).first()
    
    modifiable = not (hasattr(journal, 'facture') and journal.facture)
    return render(request, 'projManagement/detailJournal.html', {'journal': journal, 'modifiable': modifiable})



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

def detail_facture(request, id):
    facture = Facture.objects.filter(id=id).first()
    return render(request, 'projManagement/detailFacture.html', {'facture': facture})


def detail_ligne(request, id):
    # Récupère la ligne ou retourne une 404 si non trouvée
    ligne = Ligne.objects.filter(id=id).first()
    return render(request, 'projManagement/detailLigne.html', {'ligne': ligne})

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

def detail_prestation(request, id):
    prestation = Prestation.objects.filter(id=id).first()
    return render(request, 'projManagement/detailPrestation.html', {'prestation': prestation})

def creer_prestation(request):
    if request.method == 'POST':
        formulaire = PrestationForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('prestations'))
    else:
        formulaire = PrestationForm()
    return render(request, 'projManagement/creationPrestation.html', {'form': formulaire})
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