# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from django.forms import ModelForm
from core.forms.base import FormulaireBase
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Submit, HTML, Row, ButtonHolder, Fieldset
from crispy_forms.bootstrap import Field, FormActions, PrependedText, StrictButton
from core.utils.utils_commandes import Commandes
from core.forms.select2 import Select2MultipleWidget
from core.models import QuestionnaireQuestion
from core.widgets import DatePickerWidget, ColorPickerWidget, SliderWidget
from django.db.models import Max


def Get_controle(question=None):
    nom_controle = "question_%d" % question.pk

    if question.controle == "ligne_texte":
        ctrl = forms.CharField(label=question.label, required=False, help_text=question.texte_aide)
    elif question.controle == "bloc_texte":
        ctrl = forms.CharField(label=question.label, widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text=question.texte_aide)
    elif question.controle == "entier":
        ctrl = forms.IntegerField(label=question.label, required=False, help_text=question.texte_aide)
    elif question.controle == "decimal":
        ctrl = forms.DecimalField(label=question.label, max_digits=10, decimal_places=2, initial=0.0, required=False, help_text=question.texte_aide)
    elif question.controle == "montant":
        ctrl = forms.DecimalField(label=question.label, max_digits=10, decimal_places=2, initial=0.0, required=False, help_text=question.texte_aide)
    elif question.controle == "liste_deroulante":
        liste_choix = [(None, "---------")]
        liste_choix.extend([(choix, choix) for choix in question.choix.split(";")])
        ctrl = forms.TypedChoiceField(label=question.label, choices=liste_choix, initial=None, required=False, help_text=question.texte_aide)
    elif question.controle == "liste_coches":
        liste_choix = [(choix, choix) for choix in question.choix.split(";")]
        ctrl = forms.TypedMultipleChoiceField(label=question.label, choices=liste_choix, widget=Select2MultipleWidget(), required=False, help_text=question.texte_aide)
    elif question.controle == "case_coche":
        ctrl = forms.BooleanField(label=question.label, required=False, help_text=question.texte_aide)
    elif question.controle == "date":
        ctrl = forms.DateField(label=question.label, required=False, widget=DatePickerWidget(), help_text=question.texte_aide)
    elif question.controle == "slider":
        ctrl = forms.IntegerField(label=question.label, required=False, widget=SliderWidget(), help_text=question.texte_aide)
    elif question.controle == "couleur":
        ctrl = forms.CharField(label=question.label, required=False, widget=ColorPickerWidget(), help_text=question.texte_aide)
    elif question.controle == "codebarres":
        ctrl = forms.CharField(label=question.label, required=False, help_text=question.texte_aide)
    else:
        ctrl = None

    return (nom_controle, ctrl)

class Formulaire(FormulaireBase, ModelForm):
    class Meta:
        model = QuestionnaireQuestion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        categorie = kwargs.pop("categorie")
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'questions_form'
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        # Ordre
        if self.instance.ordre == None:
            max = QuestionnaireQuestion.objects.filter(categorie=categorie).aggregate(Max('ordre'))['ordre__max']
            if max == None:
                max = 0
            self.fields['ordre'].initial = max + 1
        else:
            self.fields['ordre'].initial = self.instance.ordre

        # Empêche la modification de contrôle
        if self.instance.pk:
            self.fields["controle"].disabled = True

        # Affichage
        self.helper.layout = Layout(
            Commandes(annuler_url="{{ view.get_success_url }}"),
            Hidden('categorie', value=categorie),
            Hidden('ordre', value=self.fields['ordre'].initial),
            Field('label'),
            Field('controle'),
            Field('choix'),
            Field('texte_aide'),
            Field('structure'),
            Field('visible'),
            Field('visible_portail'),
            Field('visible_fiche_renseignement'),
            HTML(EXTRA_SCRIPT),
        )

    def clean(self):
        # Individu
        if self.cleaned_data["controle"] in ("liste_deroulante", "liste_coches") and not self.cleaned_data["choix"]:
            self.add_error("choix", "Vous devez saisir au moins un choix")
            return

        return self.cleaned_data



EXTRA_SCRIPT = """
<script>

// Lors de la sélection du type de contrôle
function On_change_controle() {
    $("div[id^='div_id_ctrl']").hide();
    $('#div_id_ctrl_' + $(this).val()).show();
    $("#div_id_choix").hide();
    if (jQuery.inArray($('#id_controle').val(), ['liste_deroulante', 'liste_coches']) !== -1 ) {
        $("#div_id_choix").show();
    };
}
$(document).ready(function() {
    $('#id_controle').change(On_change_controle);
    On_change_controle.call($('#id_controle').get(0));
});

</script>
"""