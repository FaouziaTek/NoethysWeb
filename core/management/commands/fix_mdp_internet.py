# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.core.management.base import BaseCommand
from core.models import Famille, Utilisateur , Individu

class Command(BaseCommand):
    help = 'Correction des mdp internet'

    def handle(self, *args, **kwargs):
        """ Associe de nouveau les codes familles avec la table utilisateur """
        if Famille.objects.select_related("utilisateur") :
            for famille in Famille.objects.select_related("utilisateur"):

                if not famille.utilisateur:

                    # Création de l'utilisateur s'il n'existe pas déjà
                    utilisateur = Utilisateur(username=famille.internet_identifiant, categorie="famille", force_reset_password=True)
                    utilisateur.save()
                    utilisateur.set_password(famille.internet_mdp)
                    utilisateur.save()
                    famille.utilisateur = utilisateur
                    famille.save()
                    famille.utilisateur.save()

                else:

                    # Correction de l'identifiant
                    if famille.utilisateur.username != famille.internet_identifiant:
                        famille.utilisateur.username = famille.internet_identifiant

                    # Correction du mot de passe
                    if not famille.internet_mdp.startswith("custom"):
                        famille.utilisateur.set_password(famille.internet_mdp)
                        famille.utilisateur.force_reset_password = True

                    famille.utilisateur.save()

        if Individu.objects.select_related("utilisateur"):
            """ Associe de nouveau les codes individus avec la table utilisateur """
            for individu in Individu.objects.select_related("utilisateur"):

                if not individu.utilisateur:

                    # Création de l'utilisateur s'il n'existe pas déjà
                    utilisateur = Utilisateur(username=individu.internet_identifiant, categorie="individu",
                                              force_reset_password=True)
                    utilisateur.save()
                    utilisateur.set_password(individu.internet_mdp)
                    utilisateur.save()
                    individu.utilisateur = utilisateur
                    individu.save()
                    individu.utilisateur.save()

                else:

                    # Correction de l'identifiant
                    if individu.utilisateur.username != individu.internet_identifiant:
                        individu.utilisateur.username = individu.internet_identifiant

                    # Correction du mot de passe
                    if not individu.internet_mdp.startswith("custom"):
                        individu.utilisateur.set_password(individu.internet_mdp)
                        individu.utilisateur.force_reset_password = True

                    individu.utilisateur.save()

        self.stdout.write(self.style.SUCCESS("Correction des mdp internet OK"))
