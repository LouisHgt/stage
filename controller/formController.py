import os
import gc
from ..view.formView import formView
from ..model.coucheModel import coucheModel
from ..model import configModel
# --- Imports Qt ---
from qgis.PyQt import QtWidgets # type: ignore

# --- Imports QGIS Core ---
from qgis.core import QgsTask, QgsApplication, QgsMessageLog, Qgis # type: ignore

# Tâche parallele
class GenerationRapportTask(QgsTask):
    """Tâche QGIS pour générer le rapport en arrière-plan."""

    def __init__(self, description, couche_model, rapport_controller, formView, combo_values, checkbox_values, dialog_reference):
        """
        Constructeur de la tâche.

        :param description: Texte affiché dans le gestionnaire de tâches QGIS.
        :param couche_model: Instance de coucheModel.
        :param rapport_controller: Instance de rapportController.
        :param combo_values: Dictionnaire des valeurs des combobox.
        :param checkbox_values: Dictionnaire des valeurs des checkbox.
        :param dialog_reference: Référence à la boîte de dialogue (pour la fermer/modifier).
        """
        super().__init__(description, QgsTask.CanCancel) # Permet l'annulation
        self.couche_model = couche_model
        self.rapport_controller = rapport_controller
        self.formView = formView
        self.combo_values = combo_values
        self.checkbox_values = checkbox_values
        self.dialog = dialog_reference # Garde une référence à la dialog
        self.exception = None # Pour stocker une éventuelle exception
        
        
    def run(self):
        print("dans run")
        """Le code exécuté en arrière-plan. DOIT retourner True en cas de succès, False sinon."""
        QgsMessageLog.logMessage("Début de la tâche de génération du rapport.", "MonPlugin", Qgis.Info)
        try:
            total_steps = 5 # Nombre total d'étapes pour la progression
            current_step = 0

            # Étape 1: Nettoyer Tmp
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            QgsMessageLog.logMessage("Étape 1/5: Nettoyage du dossier temporaire...", "MonPlugin", Qgis.Info)
            self.couche_model.clearTmpFolder()
            current_step += 1

            # Étape 2: Créer Status Sensibilité
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            QgsMessageLog.logMessage("Étape 2/5: Création couche statut sensibilité...", "MonPlugin", Qgis.Info)
            self.couche_model.createStatusSensibilite(self.checkbox_values)
            current_step += 1

            # Étape 3: Créer Status Scénario
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            QgsMessageLog.logMessage("Étape 3/5: Création couche statut scénario...", "MonPlugin", Qgis.Info)
            self.couche_model.createStatusScenario(self.combo_values)
            current_step += 1

            # Étape 4: Créer Site Retenu
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            QgsMessageLog.logMessage("Étape 4/5: Création couche site retenu (SQL)...", "MonPlugin", Qgis.Info)
            self.couche_model.createSiteRetenu()
            current_step += 1

            """
            # Étape 5: Construire le Rapport
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            QgsMessageLog.logMessage("Étape 5/5: Génération du document rapport...", "MonPlugin", Qgis.Info)
            self.rapport_controller.buildRapport(".docx")
            current_step += 1

            # Étape finale: Garbage Collection
            if self.isCanceled(): return False
            QgsMessageLog.logMessage("Nettoyage mémoire...", "MonPlugin", Qgis.Info)
            gc.collect()

            self.setProgress(100) # Tâche terminée
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            """
            QgsMessageLog.logMessage("Tâche de génération terminée avec succès.", "MonPlugin", Qgis.Success)
            return True # Succès
            

        except Exception as e:
            self.exception = e # Stocker l'exception pour l'afficher dans finished()
            QgsMessageLog.logMessage(f"Erreur pendant la tâche : {e}", "MonPlugin", Qgis.Critical)
            return False # Échec


    def finished(self, result):
        """Exécuté dans le thread principal après la fin de run()."""
        # Récupérer le bouton Valider de la dialogue
        boutonValider = self.dialog.findChild(QtWidgets.QPushButton, 'valider')

        if result:
            self.rapport_controller.buildRapport(".docx")
            # La tâche s'est terminée avec succès (run a retourné True)
            QgsMessageLog.logMessage("Tâche terminée avec succès, fermeture de la fenêtre.", "MonPlugin", Qgis.Info)
            # Fermer la dialogue
            self.dialog.accept()
        else:
            # La tâche a échoué (run a retourné False) ou a été annulée
            if self.exception:
                # Une exception s'est produite
                QgsMessageLog.logMessage(f"La tâche a échoué : {self.exception}", "MonPlugin", Qgis.Critical)
                QtWidgets.QMessageBox.critical(self.dialog, "Erreur de Tâche", f"Une erreur est survenue durant la génération :\n\n{self.exception}")
            elif self.isCanceled():
                 QgsMessageLog.logMessage("La tâche a été annulée par l'utilisateur.", "MonPlugin", Qgis.Warning)
                 QtWidgets.QMessageBox.warning(self.dialog, "Tâche Annulée", "La génération du rapport a été annulée.")
            else:
                 # Échec inconnu
                 QgsMessageLog.logMessage("La tâche a échoué pour une raison inconnue.", "MonPlugin", Qgis.Critical)
                 QtWidgets.QMessageBox.critical(self.dialog, "Erreur Inconnue", "La tâche a échoué sans retourner d'erreur spécifique.")

            # Très important : Réactiver le bouton en cas d'échec ou d'annulation
            if boutonValider:
                boutonValider.setEnabled(True)
                boutonValider.setText('Valider') # Remettre le texte initial



# FORM CLASS -------------------------------------------------------------------
class formController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.dialog = dialog
        # Stocker les instances reçues
        self.coucheModel = couche_model_inst
        self.configModel = config_model_inst
        self.rapportController = rapport_controller_inst # Utilise l'instance reçue

        # Instancier la vue en passant les instances
        self.formView = formView(dialog, self.coucheModel, self.configModel, self.rapportController)
        # Note: Si la vue n'a besoin que du contrôleur, passez seulement le contrôleur.
        # Adaptez en fonction des besoins réels de la vue.mView = formView(dialog, coucheModel, configModel)

        self.current_task = None
    
    def setupFormulaires(self):
        """Configure les formulaires."""
        self.formView.setupFormulaireScenario()
        self.formView.setupFormulaireSensibilite()
        self.formView.setupButtons(self)
        
    def pressed(self, boutonValider):
        """
            Affiche les données et les inscrit dans des couches
            Crée le rapport docx
            Ferme la boite de dialogue
        """
        
        # print(self.getComboBoxValues())
        # print(self.getCheckboxValues())
           
        boutonValider.setEnabled(False)
        boutonValider.setText('Traitement...')
        self.formView.setupProgressBar()

        # Récupérer les valeurs nécessaires du formulaire
        combo_values = self.formView.getComboBoxValues()
        checkbox_values = self.formView.getCheckboxValues()             
        # 3. Créer l'instance de la tâche
        task_description = "Génération du rapport DDTM"
        self.current_task = GenerationRapportTask(
            task_description,
            self.coucheModel,
            self.rapportController,
            self.formView,
            combo_values,
            checkbox_values,
            self.dialog # Passe la référence de la dialog à la tâche
        )

        # Ajouter la tâche au gestionnaire de tâches de QGIS
        QgsApplication.taskManager().addTask(self.current_task)
