from django.db import models

class Client(models.Model):
    # Informations de base
    nom = models.CharField(max_length=100, verbose_name="Nom du client")
    prenom = models.CharField(max_length=100, verbose_name="Prénom du client")
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    telephone = models.CharField(max_length=20, verbose_name="Numéro de téléphone", blank=True, null=True)
    
    # Adresse
    adresse = models.CharField(max_length=255, verbose_name="Adresse", blank=True, null=True)
    ville = models.CharField(max_length=100, verbose_name="Ville", blank=True, null=True)
    code_postal = models.CharField(max_length=10, verbose_name="Code postal", blank=True, null=True)
    pays = models.CharField(max_length=100, verbose_name="Pays", blank=True, null=True)
    
    # Informations supplémentaires
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    actif = models.BooleanField(default=True, verbose_name="Client actif")
    
    # Méthode pour afficher le nom complet du client
    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Mission(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre de la mission")
    description = models.TextField(blank=True, null=True, verbose_name="Description de la mission")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name="missions", verbose_name="Client", null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.client.prenom if self.client else 'Aucun client'} {self.client.nom if self.client else ''})"