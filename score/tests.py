from django.test import TestCase
from score.models import ListeJoueurs
from score.views import determiner_role_president
from django.urls import reverse

class ListeJoueursTestCase(TestCase):
    def test_numero_auto_incremente(self):
        joueur1 = ListeJoueurs.objects.create(joueurNom="Axel")
        joueur2 = ListeJoueurs.objects.create(joueurNom="Chloe")   
        self.assertEqual(joueur1.joueurNum, 1)
        self.assertEqual(joueur2.joueurNum, 2)

    def test_couleur_attribuee_automatiquement(self):
        joueur = ListeJoueurs.objects.create(joueurNom="Axel")
        self.assertNotEqual(joueur.couleur, '')

class RolePresidentTestCase(TestCase):
    def test_president_a_2_joueurs(self): # Doit valoir Président et Trouduc car 2 joueurs
        self.assertEqual(determiner_role_president(1, 2), 'Président')
        self.assertEqual(determiner_role_president(2, 2), 'Trouduc')
    
    def test_president_a_3_joueurs(self):  # Doit valoir Suisse car 2e joueur sur 3 au total
        self.assertEqual(determiner_role_president(2, 3), 'Suisse')

    def test_president_a_4_joueurs(self):  # Doit valoir Vice-Président et Vice-Trouduc car 2 et 3e joueurs sur 4 au total
        self.assertEqual(determiner_role_president(2, 4), 'Vice-Président')
        self.assertEqual(determiner_role_president(3, 4), 'Vice-Trouduc')

class AccueilTestCase(TestCase):
    def test_accueil_accessible(self):
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 200)