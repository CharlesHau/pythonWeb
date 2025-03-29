from django.contrib import admin
from projManagement.models import Client, Mission,Journal,Facture,Prestation,Ligne,Collaborateur,FeuilleDeTemps,LigneDeFeuilleDeTemps,Paiement, TaskWorkflow, TaskAssignment
# Register your models here.
admin.site.register(Client)
admin.site.register(Mission)
admin.site.register(Journal)
admin.site.register(Facture)
admin.site.register(Prestation)
admin.site.register(Ligne)
admin.site.register(Collaborateur)
admin.site.register(FeuilleDeTemps)
admin.site.register(LigneDeFeuilleDeTemps)
admin.site.register(Paiement)
admin.site.register(TaskAssignment)
admin.site.register(TaskWorkflow)

