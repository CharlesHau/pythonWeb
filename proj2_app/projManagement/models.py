from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password


class Collaborateur(models.Model):
    class Role(models.TextChoices):
        COMPTABLE = 'COMPTABLE', 'Comptable'
        DIRECTEUR = 'RAF', 'Responsable administratif et financier'
        ASSOCIE = 'ASSOCIE', 'Associé'
        AGI = 'AGI', 'Assistant de gestion'

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=Role.choices)
    tarif_horaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def set_password(self, raw_password):
        """
        Hache le mot de passe fourni en utilisant les fonctions de Django
        """
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        """
        Vérifie si le mot de passe fourni correspond au mot de passe stocké
        """
        return check_password(raw_password, self.password)
        
    def save(self, *args, **kwargs):
        """
        Surcharge la méthode save pour s'assurer que le mot de passe est toujours haché
        """
        # Si le mot de passe n'est pas haché (n'a pas le format bcrypt, pbkdf2, etc.)
        if self.password and not self.password.startswith(('pbkdf2_', 'bcrypt')):
            self.set_password(self.password)
        super().save(*args, **kwargs)

class FeuilleDeTemps(models.Model):
    mission = models.ForeignKey('Mission', on_delete=models.CASCADE, related_name='feuilles_de_temps')
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE, related_name='feuilles_de_temps')
    date_creation = models.DateField(default=now, editable=True)

    def __str__(self):
        return f"Feuille de temps de {self.collaborateur} pour la mission {self.mission}"
    
class LigneDeFeuilleDeTemps(models.Model):
    feuille_de_temps = models.ForeignKey(FeuilleDeTemps, on_delete=models.CASCADE, related_name='lignes')
    date = models.DateField()
    heures_travaillees = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.heures_travaillees} heures le {self.date} - {self.description}"
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
    logo = models.ImageField(upload_to='client_logos/', null=True, blank=True)

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
    description = models.TextField(editable=True, blank=True, null=True)

    def __str__(self):
        return f"Journal de la mission {self.mission.title}"

class Facture(models.Model):
    journal = models.OneToOneField(Journal, on_delete=models.CASCADE, related_name="facture")
    date_emission = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=[("impayé", "Impayé"), ("payé", "Payé"), ("en retard", "En retard")], default='Impayé')
    

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

    @property
    def prix_total(self):
        return self.prestation.prix * self.quantite
    
    def __str__(self):
        return f"{self.quantite} x {self.prestation.description}"
# Dans models.py

class Paiement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name="paiements")
    date_paiement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Méthodes de paiement possibles
    MODE_PAIEMENT_CHOICES = [
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces'),
        ('cb', 'Carte bancaire'),
    ]
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='virement')
    
    # Commentaire optionnel
    commentaire = models.TextField(blank=True, null=True)
    
    # Pour savoir quand le paiement a été enregistré
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_paiement']  # Les paiements les plus récents en premier
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
    
    def __str__(self):
        return f"Paiement de {self.montant}€ du {self.date_paiement} pour facture #{self.facture.id}"
    
    def save(self, *args, **kwargs):
        # Mettre à jour le statut de la facture si nécessaire
        super().save(*args, **kwargs)
        self.update_facture_status()
    
    def update_facture_status(self):
        """
        Met à jour le statut de la facture en fonction des paiements.
        """
        facture = self.facture
        total_paiements = sum(p.montant for p in facture.paiements.all())
        
        # Si le total des paiements est supérieur ou égal au montant de la facture
        if total_paiements >= facture.montant_total:
            facture.statut = 'payé'
            facture.save()
        # Sinon, si au moins un paiement a été effectué mais pas la totalité
        elif total_paiements > 0:
            facture.statut = 'partiellement payé'
            facture.save()