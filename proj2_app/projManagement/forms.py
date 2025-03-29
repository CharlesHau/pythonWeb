# -*- coding: utf-8 -*-

from django import forms
from .models import Client, Mission, Journal, Ligne, Prestation, Facture,Collaborateur,FeuilleDeTemps,LigneDeFeuilleDeTemps, Paiement


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'email', 'telephone', 'adresse', 'ville', 'code_postal', 'pays', 'logo']
        #aucune idée de pourquoi je peux pas enregistrer d'image
        # pourquoi le modèle est correcte, le formulaire de saisie a le bon attribut
        
class CollaborateurForm(forms.ModelForm):
    class Meta:
        model = Collaborateur
        fields = ['nom', 'prenom', 'email', 'role', 'tarif_horaire']
class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['title', 'description', 'start_date', 'end_date', 'client', 'libelle', 'budget', 'statut']
        widgets = {
           'start_date': forms.DateInput(attrs={'type': 'date'}),
           'end_date': forms.DateInput(attrs={'type': 'date'}),
       }
class FeuilleDeTempsForm(forms.ModelForm):
    class Meta:
        model = FeuilleDeTemps
        fields = ['mission', 'collaborateur', 'date_creation']
        widgets = {
            'date_creation': forms.DateInput(attrs={'type': 'date'}),
        }
class JournalForm(forms.ModelForm):
    
    class Meta:
        model = Journal
        fields = ['mission', 'statut','description']

class LigneForm(forms.ModelForm):
    class Meta:
        model = Ligne
        fields = [ 'prestation', 'date', 'description', 'quantite']
        widgets = {
           'date': forms.DateInput(attrs={'type': 'date'}),
       }
        
class LigneFeuilleDeTempsForm(forms.ModelForm):
    class Meta:
        model = LigneDeFeuilleDeTemps
        fields = ['date', 'description', 'heures_travaillees' ]
        widgets = {
           'date': forms.DateInput(attrs={'type': 'date'}),
       }

class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        fields = ['diminutif', 'description', 'prix']

class FactureForm(forms.ModelForm):
    date_emission = forms.DateField(disabled=True, required=False)
    class Meta:
        model = Facture
        fields = ['journal']


class RechercheMissionForm(forms.Form):
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Date de début (à partir de)"          
        )
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Date de fin (jusqu'au)"   
        )
    budget_min = forms.DecimalField(
        required=False,
        label="Budget minimal"
        )
    budget_max = forms.DecimalField(
        required=False,
        label="Budget maximal"
        )
    statut_mission = forms.CharField(
        required=False,
        label="Statut de la mission"
        )
    class Meta:
        widgets = {
           'date': forms.DateInput(attrs={'type': 'date'}),
       }
# Dans forms.py

class PaiementForm(forms.ModelForm):
    """Formulaire pour créer ou modifier un paiement."""
    
    class Meta:
        model = Paiement
        fields = ['date_paiement', 'montant', 'reference', 'mode_paiement', 'commentaire']
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        # On peut passer une facture en paramètre pour préremplir le montant
        facture = kwargs.pop('facture', None)
        super().__init__(*args, **kwargs)
        
        if facture:
            # Calculer le montant restant à payer
            total_paye = sum(p.montant for p in facture.paiements.all())
            montant_restant = facture.montant_total - total_paye
            
            # Préremplir le montant avec le reste à payer
            self.fields['montant'].initial = montant_restant