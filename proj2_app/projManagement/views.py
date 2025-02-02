from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Client, Mission, Journal, Facture, Prestation
from .forms import ClientForm, MissionForm, FactureForm, PrestationForm,JournalForm, LigneForm
from django.urls import reverse
from django.utils.timezone import now
# Create your views here.

def index(request):
    return HttpResponse('<H1> hello all</h1>')

def clients(request):
    clients_list = Client.objects.all()
    return render(request, 'projManagement/clients.html', {'clients': clients_list})
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


def home(request):
    missions_actives = Mission.objects.filter(statut='en cours').count()
    factures_en_attente = Facture.objects.filter(montant_total__gt=0).count()
    total_clients = Client.objects.count()
    total_journaux = Journal.objects.count()
    
    context = {
        'missions_actives': missions_actives,
        'factures_en_attente': factures_en_attente,
        'total_clients': total_clients,
        'total_journaux': total_journaux
    }
    return render(request, 'projManagement/home.html', context)

def missions(request):
    missions_list = Mission.objects.all()
    return render(request, 'projManagement/missions.html', {'missions': missions_list})

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

def journaux(request):
    journaux_list = Journal.objects.all()
    return render(request, 'projManagement/journaux.html', {'journaux': journaux_list})
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
    return render(request, 'projManagement/detailJournal.html', {'journal': journal})
def factures(request):
    factures_list = Facture.objects.all()
    return render(request, 'projManagement/factures.html', {'factures': factures_list})
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
    prestations_list = Prestation.objects.all()
    return render(request, 'projManagement/prestations.html', {'prestations': prestations_list})
def creer_prestation(request):
    if request.method == 'POST':
        formulaire = PrestationForm(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return HttpResponseRedirect(reverse('prestations'))
    else:
        formulaire = PrestationForm()
    return render(request, 'projManagement/creationPrestation.html', {'form': formulaire})