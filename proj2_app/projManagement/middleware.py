# -*- coding: utf-8 -*-

import logging
from django.shortcuts import redirect
from django.urls import reverse
from .models import Collaborateur
logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("Initialisation du middleware d'authentification")

    def __call__(self, request):
        # URLs exclues du middleware (page de connexion/déconnexion)
        exempt_urls = [reverse('login'), reverse('logout')]
        
        # Si l'URL actuelle est exemptée, ne pas vérifier l'authentification
        if request.path in exempt_urls:
            logger.debug(f"URL exemptée de l'authentification: {request.path}")
            return self.get_response(request)
        
        # Vérifier si l'utilisateur est connecté
        collaborateur_id = request.session.get('collaborateur_id')
        if not collaborateur_id:
            logger.warning(f"Tentative d'accès à {request.path} sans authentification - Redirection vers login")
            return redirect('login')
        
        # Ajouter le collaborateur à la requête
        try:
            request.collaborateur = Collaborateur.objects.get(id=collaborateur_id)
            logger.debug(f"Collaborateur {request.collaborateur.email} authentifié pour {request.path}")
        except Collaborateur.DoesNotExist:
            # Si le collaborateur n'existe plus en base, supprimer la session
            logger.error(f"Collaborateur avec ID {collaborateur_id} non trouvé en base - Session invalide")
            del request.session['collaborateur_id']
            return redirect('login')
        
        # Continuer le traitement de la requête
        return self.get_response(request)
    
class RoleCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Définir les restrictions d'accès par URL et rôle
        self.role_requirements = {
            'journaux': ['COMPTABLE', 'RAF', 'ASSOCIE'],
            'factures': ['RAF', 'ASSOCIE'],
            'missions': ['ASSOCIE'],
            # Ajoutez d'autres URLs et rôles selon vos besoins
        }

    def __call__(self, request):
        # Ne vérifier les rôles que si l'utilisateur est authentifié
        if hasattr(request, 'collaborateur'):
            # Extraire le premier segment de l'URL (après le premier slash)
            # Par exemple, pour /journaux/123/, cela donnerait "journaux"
            url_segment = request.path.strip('/').split('/')[0]
            
            # Vérifier si cette URL a des restrictions de rôle
            if url_segment in self.role_requirements:
                required_roles = self.role_requirements[url_segment]
                
                # Si le rôle du collaborateur n'est pas dans les rôles requis
                if request.collaborateur.role not in required_roles:
                    # Rediriger vers une page d'accès refusé
                    return redirect('access_denied')
        
        # Continuer le traitement de la requête
        return self.get_response(request)