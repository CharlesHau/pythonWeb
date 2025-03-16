# Dans decorators.py

import logging
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

# Configurer le logger
logger = logging.getLogger(__name__)

def login_required(view_func):
    """
    Décorateur qui vérifie si l'utilisateur est connecté.
    Si ce n'est pas le cas, il est redirigé vers la page de connexion.
    
    Note: Ce décorateur est généralement redondant avec le middleware
    d'authentification, mais peut être utile pour des vues spécifiques.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vérifier si l'utilisateur est connecté
        if not request.session.get('collaborateur_id'):
            logger.warning(f"Accès refusé à {request.path}: utilisateur non connecté")
            return redirect('login')
        
        logger.debug(f"Accès autorisé à {request.path}: utilisateur connecté")
        return view_func(request, *args, **kwargs)
    
    return wrapper

def role_required(allowed_roles):
    """
    Décorateur qui vérifie si l'utilisateur a l'un des rôles autorisés.
    Si ce n'est pas le cas, il est redirigé vers une page d'accès refusé.
    
    @param allowed_roles: Liste des rôles autorisés
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Vérifier si l'utilisateur est connecté et si le collaborateur est chargé
            if not hasattr(request, 'collaborateur'):
                logger.warning(f"Accès refusé à {request.path}: utilisateur non connecté")
                return redirect('login')
            
            # Vérifier si le rôle de l'utilisateur est autorisé
            if request.collaborateur.role not in allowed_roles:
                logger.warning(
                    f"Accès refusé à {request.path}: rôle insuffisant ({request.collaborateur.role})"
                )
                return redirect('access_denied')
            
            logger.debug(f"Accès autorisé à {request.path}: rôle {request.collaborateur.role} autorisé")
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator

# Décorateurs spécifiques pour chaque rôle
def comptable_required(view_func):
    """Décorateur pour restreindre l'accès aux comptables, RAF et associés"""
    return role_required(['COMPTABLE', 'RAF', 'ASSOCIE'])(view_func)

def raf_required(view_func):
    """Décorateur pour restreindre l'accès aux RAF et associés"""
    return role_required(['RAF', 'ASSOCIE'])(view_func)

def associe_required(view_func):
    """Décorateur pour restreindre l'accès aux associés uniquement"""
    return role_required(['ASSOCIE'])(view_func)