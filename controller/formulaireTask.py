from qgis.core import QgsTask, QgsApplication, QgsMessageLog, Qgis # type: ignore
from qgis.PyQt import QtWidgets # type: ignore
from qgis.PyQt.QtCore import pyqtSignal # type: ignore

class formulaireTask(QgsTask):
    """Tâche QGIS pour générer le rapport en arrière-plan."""

    # Signal de fin de tache
    task_finished = pyqtSignal(bool)   
     
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
        """Le code exécuté en arrière-plan. DOIT retourner True en cas de succès, False sinon."""
        QgsMessageLog.logMessage("Début de la tâche de recuperation des données selon le formulaire.", "MonPlugin", Qgis.Info)
        try:
            total_steps = 4 # Nombre total d'étapes pour la progression
            current_step = 0

            # Étape 1: Nettoyer Tmp
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.couche_model.clearTmpFolder() # Action de l'etape
            current_step += 1
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar


            # Étape 2: Créer Status Sensibilité
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.couche_model.createStatusSensibilite(self.checkbox_values) # Action de l'etape
            current_step += 1
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar


            # Étape 3: Créer Status Scénario
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.couche_model.createStatusScenario(self.combo_values) # Action de l'etape
            current_step += 1
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar


            # Étape 4: Créer Site Retenu
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            self.couche_model.createSiteRetenu()
            current_step += 1
            self.formView.setProgressBarValue(current_step) # Actualisation de la progressBar
            self.setProgress(current_step / total_steps * 100)
            
            return True
            
            

        except Exception as e:
            self.exception = e # Stocker l'exception pour l'afficher dans finished()
            QgsMessageLog.logMessage(f"Erreur pendant la tâche : {e}", "MonPlugin", Qgis.Critical)
            return False # Échec


    def finished(self, result):
        """Exécuté dans le thread principal après la fin de run()."""
        # Récupérer le bouton Valider de la dialogue
        boutonValider = self.dialog.findChild(QtWidgets.QPushButton, 'valider')

        if result:
            self.task_finished.emit(True) # Signal fin de tâche
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
