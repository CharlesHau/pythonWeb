from django.db import models
from django.utils.timezone import now

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Mission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="missions")
    libelle = models.CharField(max_length=255, default = '')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=[("en cours", "En cours"), ("en attente", "En attente"), ("fermé", "Fermé")], default='En attente')

    def __str__(self):
        return f"{self.title} ({self.client.prenom if self.client else 'Aucun client'} {self.client.nom if self.client else ''})"

class Journal(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="journaux")
    statut = models.CharField(max_length=20, choices=[("brouillon", "Brouillon"), ("validé", "Validé")])
    date_creation = models.DateField(default=now, editable=False)

    def __str__(self):
        return f"Journal de la mission {self.mission.title}"

class Facture(models.Model):
    journal = models.OneToOneField(Journal, on_delete=models.CASCADE, related_name="facture")
    date_emission = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Facture pour {self.journal.mission.title}"

class Prestation(models.Model):
    diminutif = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description

class Ligne(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name="lignes")
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE, related_name="lignes")
    date = models.DateField()
    description = models.TextField()
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.quantite} x {self.prestation.description}"
