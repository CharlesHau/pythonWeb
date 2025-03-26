from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .models import Collaborateur, Journal, Mission, Client as ClientModel, Facture
from django.utils.timezone import now
from .views import creer_facture
from .middleware import AuthenticationMiddleware

class FactureAccessTests(TestCase):
    def setUp(self):
        """
        Préparation des données de test.
        """
        # Créer des utilisateurs avec différents rôles
        self.comptable = Collaborateur.objects.create(
            nom="Comptable",
            prenom="Test",
            email="comptable@test.com",
            role="COMPTABLE",
            tarif_horaire=50.0
        )
        self.comptable.set_password("password123")
        self.comptable.save()
        
        self.raf = Collaborateur.objects.create(
            nom="RAF",
            prenom="Test",
            email="raf@test.com",
            role="RAF",
            tarif_horaire=75.0
        )
        self.raf.set_password("password123")
        self.raf.save()
        
        self.associe = Collaborateur.objects.create(
            nom="Associe",
            prenom="Test",
            email="associe@test.com",
            role="ASSOCIE",
            tarif_horaire=100.0
        )
        self.associe.set_password("password123")
        self.associe.save()
        
        # Créer un client
        self.client_model = ClientModel.objects.create(
            nom="Client",
            prenom="Test",
            email="client@test.com"
        )
        
        # Créer une mission
        self.mission = Mission.objects.create(
            title="Mission test",
            description="Description de test",
            start_date=now().date(),
            client=self.client_model,
            statut="en cours"
        )
        
        # Créer un journal
        self.journal = Journal.objects.create(
            mission=self.mission,
            statut="validé"
        )
        
        # Créer un client HTTP pour les tests
        self.client_http = Client()
        self.factory = RequestFactory()

    def test_login_comptable(self):
        """
        Test de connexion en tant que comptable
        """
        # Connexion via la vue de login
        response = self.client_http.post(reverse('login'), {
            'email': 'comptable@test.com',
            'password': 'password123'
        }, follow=True)
        
        # Vérifier que la connexion a réussi
        self.assertEqual(response.status_code, 200)
        self.assertIn('collaborateur_id', self.client_http.session)
        self.assertEqual(self.client_http.session['collaborateur_id'], self.comptable.id)
        
        # Vérifier que l'accès à la page de création de facture est refusé
        response = self.client_http.get(reverse('creer_facture'), follow=True)
        self.assertTemplateUsed(response, 'registration/access_denied.html')
        
    def test_login_raf(self):
        """
        Test de connexion en tant que RAF et création de facture
        """
        # Connexion via la vue de login
        response = self.client_http.post(reverse('login'), {
            'email': 'raf@test.com', 
            'password': 'password123'
        }, follow=True)
        
        # Vérifier que la connexion a réussi
        self.assertEqual(response.status_code, 200)
        self.assertIn('collaborateur_id', self.client_http.session)
        self.assertEqual(self.client_http.session['collaborateur_id'], self.raf.id)
        
        # Accéder à la page de création de facture
        response = self.client_http.get(reverse('creer_facture'))
        self.assertEqual(response.status_code, 200)
        
        # Créer une facture
        response = self.client_http.post(
            reverse('creer_facture'),
            {'journal': self.journal.id},
            follow=True
        )
        
        # Vérifier la redirection et la création
        self.assertTemplateUsed(response, 'projManagement/factures.html')
        self.assertTrue(Facture.objects.filter(journal=self.journal).exists())
    def test_comptable_cannot_create_facture(self):
        """
        Test qu'un comptable ne peut pas créer de facture.
        """
        # Simuler une connexion en tant que comptable
        session = self.client_http.session
        session['collaborateur_id'] = self.comptable.id
        session['collaborateur_role'] = self.comptable.role
        session.save()
        
        # Tenter d'accéder à la page de création de facture
        response = self.client_http.get(reverse('creer_facture'))
        
        # Vérifier la redirection vers la page d'accès refusé
        self.assertRedirects(response, reverse('access_denied'))
        
        # Tenter de créer une facture via POST
        response = self.client_http.post(
            reverse('creer_facture'),
            {'journal': self.journal.id}
        )
        
        # Vérifier la redirection vers la page d'accès refusé
        self.assertRedirects(response, reverse('access_denied'))
    
    def test_raf_can_create_facture(self):
        """
        Test qu'un RAF peut créer une facture.
        """
        # Simuler une connexion en tant que RAF
        session = self.client_http.session
        session['collaborateur_id'] = self.raf.id
        session['collaborateur_role'] = self.raf.role
        session.save()
        
        # Accéder à la page de création de facture
        response = self.client_http.get(reverse('creer_facture'))
        
        # Vérifier que la page est accessible (code 200)
        self.assertEqual(response.status_code, 200)
        
        # Créer une facture via POST
        response = self.client_http.post(
            reverse('creer_facture'),
            {'journal': self.journal.id}
        )
        
        # Vérifier la redirection vers la liste des factures après création
        self.assertRedirects(response, reverse('factures'))
        
        # Vérifier qu'une facture a été créée dans la base de données
        self.assertEqual(self.journal.facture.id is not None, True)
    
    def test_associe_can_create_facture(self):
        """
        Test qu'un associé peut également créer une facture.
        """
        # Simuler une connexion en tant qu'associé
        session = self.client_http.session
        session['collaborateur_id'] = self.associe.id
        session['collaborateur_role'] = self.associe.role
        session.save()
        
        # Accéder à la page de création de facture
        response = self.client_http.get(reverse('creer_facture'))
        
        # Vérifier que la page est accessible
        self.assertEqual(response.status_code, 200)