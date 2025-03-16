# Dans middleware.py

import logging
from django.shortcuts import redirect
from django.urls import reverse
from .models import Collaborateur

logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    """
    Middleware qui vérifie l'authentification de l'utilisateur
    et charge le collaborateur dans l'objet request
    """
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("Initialisation du middleware d'authentification")

    def __call__(self, request):
        # Chemins exemptés de l'authentification
        exempt_paths = [
            reverse('login'), 
            reverse('logout'),
            reverse('admin:index'),  # Interface d'administration Django
            '/admin/',  # Pour couvrir tous les chemins d'administration
            '/static/',  # Fichiers statiques
        ]
        
        # Vérifier si le chemin est exempté
        path_exempt = False
        for exempt in exempt_paths:
            if request.path.startswith(exempt):
                path_exempt = True
                break
                
        if path_exempt:
            logger.debug(f"Chemin exempté de l'authentification: {request.path}")
            return self.get_response(request)
        
        # Vérifier si l'utilisateur est connecté
        collaborateur_id = request.session.get('collaborateur_id')
        if not collaborateur_id:
            logger.warning(f"Tentative d'accès à {request.path} sans authentification - Redirection vers login")
            # Stocker l'URL demandée pour y revenir après la connexion
            request.session['next_url'] = request.path
            return redirect('login')
        
        # Charger le collaborateur dans la requête
        try:
            request.collaborateur = Collaborateur.objects.get(id=collaborateur_id)
            logger.debug(f"Collaborateur {request.collaborateur.email} authentifié pour {request.path}")
        except Collaborateur.DoesNotExist:
            # Si le collaborateur n'existe plus en base, supprimer la session
            logger.error(f"Collaborateur avec ID {collaborateur_id} non trouvé en base - Session invalide")
            request.session.flush()
            return redirect('login')
        
        # Continuer le traitement de la requête
        return self.get_response(request)


class RoleCheckMiddleware:
    """
    Middleware qui vérifie les autorisations basées sur les rôles
    pour certaines sections de l'application
    """
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("Initialisation du middleware de vérification des rôles")
        
        # Définir les restrictions d'accès par chemin d'URL et rôle
        # Format: 'chemin': ['ROLE1', 'ROLE2', ...]
        self.role_requirements = {
            # Accès aux journaux : pour les comptables, RAF et associés
            'journaux': ['COMPTABLE', 'RAF', 'ASSOCIE'],
            
            # Accès aux factures : seulement pour RAF et associés
            'factures': ['RAF', 'ASSOCIE'],
            
            # Accès aux rapports : seulement pour les associés
            'missions/reporting': ['ASSOCIE'],
        }

    def __call__(self, request):
        # Ne vérifier les rôles que si l'utilisateur est authentifié
        if hasattr(request, 'collaborateur'):
            # Extraire le chemin de l'URL sans le domaine ni les paramètres
            path = request.path.strip('/')
            
            # Vérifier chaque règle de restriction
            for restricted_path, required_roles in self.role_requirements.items():
                # Si le chemin de la requête commence par le chemin restreint
                if path.startswith(restricted_path):
                    # Si le rôle du collaborateur n'est pas dans les rôles requis
                    if request.collaborateur.role not in required_roles:
                        logger.warning(
                            f"Accès refusé à {path} pour {request.collaborateur.email} "
                            f"avec le rôle {request.collaborateur.role}"
                        )
                        return redirect('access_denied')
        
        # Continuer le traitement de la requête
        return self.get_response(request)