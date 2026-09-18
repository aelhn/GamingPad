from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from score.models import ListeJoueurs
from score.views import determiner_role_president
from .models import Partie, Tour, ScoreTour, AjustementDumble
from .views import calculer_totaux_dumble

class HistoriqueTestCase(TestCase):
    def setUp(self):         # Prepare 2 joueurs et 2 parties (une terminee, une en cours) pour verifier le filtrage
        self.joueur1 = ListeJoueurs.objects.create(joueurNom="Axel")
        self.joueur2 = ListeJoueurs.objects.create(joueurNom="Chloe")

        self.partie_terminee = Partie.objects.create(
            typeJeu='flechette',
            dateFin=timezone.now(),
            gagnant=self.joueur1,
        )
        self.partie_en_cours = Partie.objects.create(typeJeu='flechette')

    def test_parties_terminees_uniquement(self): # Vérifie qu'uniquement les parties terminées n'apparaissent 
        # Exclut les lignes sans dateFin donc (car non terminées)
        response = self.client.get(reverse('historique_parties'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.joueur1.joueurNom)  # Nom du gagnant
        self.assertEqual(len(response.context['parties']), 1)  # une seule partie doit remonter

    def test_detail_par_manche(self): # Verifie que le detail d'une manche jouée (joueur + score) apparait bien
        tour = Tour.objects.create(partie=self.partie_terminee, numero=1)
        ScoreTour.objects.create(tour=tour, joueur=self.joueur1, score=100, casse=False)

        response = self.client.get(reverse('historique_parties'))
        item = response.context['parties'][0]
        self.assertEqual(len(item['tours_detail']), 1)
        self.assertEqual(item['tours_detail'][0]['numero'], 1)

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

class DumbleTestCase(TestCase):
    def setUp(self): # Setup une partie de Dumble avec 2 joueurs, réutilisés ensuite après
        self.joueur1 = ListeJoueurs.objects.create(joueurNom="Axel")
        self.joueur2 = ListeJoueurs.objects.create(joueurNom="Chloé")
        self.joueurs = ListeJoueurs.objects.filter(id__in=[self.joueur1.id, self.joueur2.id])
        self.partie = Partie.objects.create(typeJeu='dumble')

    def test_elimine_si_plus_de_100(self):
        tour = Tour.objects.create(partie=self.partie, numero=1)
        ScoreTour.objects.create(tour=tour, joueur=self.joueur1, score=105, dumble=True)
        ScoreTour.objects.create(tour=tour, joueur=self.joueur2, score=50, dumble=False)

        totaux = calculer_totaux_dumble(self.partie, self.joueurs)
        self.assertTrue(totaux[self.joueur1.id]['elimine'])
        self.assertFalse(totaux[self.joueur2.id]['elimine'])

    def test_redescend_a_50_sur_100_pile(self): # Si score = 100, redescend à 50
        tour = Tour.objects.create(partie=self.partie, numero=1)
        ScoreTour.objects.create(tour=tour, joueur=self.joueur1, score=100, dumble=True)
        ScoreTour.objects.create(tour=tour, joueur=self.joueur2, score=30, dumble=False)

        AjustementDumble.objects.create(partie=self.partie, joueur=self.joueur1, valeur=-50)

        totaux = calculer_totaux_dumble(self.partie, self.joueurs)
        self.assertEqual(totaux[self.joueur1.id]['total'], 50)
        self.assertFalse(totaux[self.joueur1.id]['elimine'])

class AccueilTestCase(TestCase):
    def test_accueil_accessible(self):
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 200)