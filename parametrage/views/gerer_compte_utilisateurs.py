#  Copyright (c) 2024 GIP RECIA.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy
from django.core.cache import cache
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from core.views.base import CustomView
from django.shortcuts import redirect, render
from parametrage.forms.gerer_compte_utilisateurs import Formulaire
import django.contrib.messages
from core.models import PortailParametre


class Modifier(CustomView, TemplateView):
    template_name = "core/crud/edit.html"
    compatible_demo = False

    def get_context_data(self, **kwargs):
        context = super(Modifier, self).get_context_data(**kwargs)
        context['page_titre'] = "Paramètres du compte utilisateurs"
        context['box_titre'] = "Paramètres Compte"
        context[
            'box_introduction'] = "Ajustez les paramètres de compte utilisateurs et cliquez sur le bouton Enregistrer."

        # # Récupérer ou initialiser les valeurs de session à partir de la base de données
        if 'compte_individu_active' not in self.request.session and 'compte_famille_active' not in self.request.session:
            # Tentative de récupération des paramètres de la base de données
            compte_individu = PortailParametre.objects.filter(code="compte_individu").first()
            compte_famille = PortailParametre.objects.filter(code="compte_famille").first()

            # Initialisez les valeurs de session en fonction des valeurs de la base de données ou par défaut sur False si elles ne sont pas trouvées
            self.request.session['compte_individu_active'] = bool(compte_individu and compte_individu.valeur == 'True')
            self.request.session['compte_famille_active'] = bool(compte_famille and compte_famille.valeur == 'True')

            # Si les paramètres n'existent pas dans la base de données, définissez-les sur False uniquement dans la session (sans créer de nouvelles entrées)
            if not compte_individu:
                self.request.session['compte_individu_active'] = False
            if not compte_famille:
                self.request.session['compte_famille_active'] = False

        # Transmettre les valeurs de session au formulaire
        initial_data = {
            "compte_individu": self.request.session.get('compte_individu_active', True),
            "compte_famille": self.request.session.get('compte_famille_active', False),
        }
        context['form'] = Formulaire(initial=initial_data)
        return context

    def post(self, request, **kwargs):
        form = Formulaire(request.POST, request=self.request)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        # Enregistrer les valeurs des paramètres dans la table PortailParamètre
        dict_parametres = {parametre.code: parametre for parametre in PortailParametre.objects.all()}
        print("dict_parametres",dict_parametres)
        for code, valeur in form.cleaned_data.items():
            if code in dict_parametres:
                dict_parametres[code].valeur = str(valeur)
                print(dict_parametres[code].valeur)
            else:
                PortailParametre.objects.create(code=code, valeur=str(valeur))
                print(PortailParametre.objects.create(code=code, valeur=str(valeur)))


        PortailParametre.objects.bulk_update(dict_parametres.values(), ["valeur"])
        cache.delete("parametres_portail")

        # Stocker les états des cases à cocher dans la session
        request.session['compte_individu_active'] = form.cleaned_data.get("compte_individu", False)
        request.session['compte_famille_active'] = form.cleaned_data.get("compte_famille", False)

        django.contrib.messages.success(request, 'Paramètres enregistrés')
        return HttpResponseRedirect(reverse_lazy("gerer_compte_utilisateurs"))
