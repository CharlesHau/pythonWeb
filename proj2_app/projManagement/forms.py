# -*- coding: utf-8 -*-

from django import forms
from .models import Client, Mission, Journal, Ligne, Prestation, Facture

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'email', 'telephone', 'adresse', 'ville', 'code_postal', 'pays']

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['title', 'description', 'start_date', 'end_date', 'client', 'libelle', 'budget', 'statut']
        widgets = {
           'start_date': forms.DateInput(attrs={'type': 'date'}),
           'end_date': forms.DateInput(attrs={'type': 'date'}),
       }
class JournalForm(forms.ModelForm):
    
    class Meta:
        model = Journal
        fields = ['mission', 'statut']

class LigneForm(forms.ModelForm):
    class Meta:
        model = Ligne
        fields = [ 'prestation', 'date', 'description', 'quantite']
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
