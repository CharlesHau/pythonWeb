# -*- coding: utf-8 -*-

import logging
from functools import wraps
from django.shortcuts import redirect


# Configurer le logger
logger = logging.getLogger(__name__)
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vérifier si l'utilisateur est connecté
        if not request.session.get('collaborateur_id'):
            logger.warning(f"Accès refusé à {request.path}: utilisateur non connecté")
            print(f"DÉCORATEUR - Accès refusé: Utilisateur non connecté pour {request.path}")
            return redirect('login')
        logger.debug(f"Accès autorisé à {request.path}: utilisateur connecté")
        return view_func(request, *args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Vérifier si l'utilisateur est connecté
            if not hasattr(request, 'collaborateur'):
                logger.warning(f"Accès refusé à {request.path}: utilisateur non connecté")
                print(f"DÉCORATEUR - Accès refusé: Utilisateur non connecté pour {request.path}")
                return redirect('login')
            
            # Vérifier si le rôle de l'utilisateur est autorisé
            if request.collaborateur.role not in allowed_roles:
                logger.warning(f"Accès refusé à {request.path}: rôle insuffisant ({request.collaborateur.role})")
                print(f"DÉCORATEUR - Accès refusé: Rôle insuffisant ({request.collaborateur.role}) pour {request.path}")
                return redirect('access_denied')
            
            logger.debug(f"Accès autorisé à {request.path}: rôle {request.collaborateur.role} autorisé")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
# Décorateurs spécifiques pour chaque rôle
def comptable_required(view_func):
    return role_required(['COMPTABLE', 'RAF', 'ASSOCIE'])(view_func)

def raf_required(view_func):
    return role_required(['RAF', 'ASSOCIE'])(view_func)

def associe_required(view_func):
    return role_required(['ASSOCIE'])(view_func)