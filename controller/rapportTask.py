
from qgis.core import QgsTask, QgsApplication, QgsMessageLog, Qgis # type: ignore
from qgis.PyQt import QtWidgets # type: ignore


class rapportTask(QgsTask):
    """Tâche QGIS pour générer le rapport en arrière-plan."""

    def __init__(self, description, rapport_controller, formView, dialog):

        super().__init__(description, QgsTask.CanCancel) # Permet l'annulation
        self.rapport_controller = rapport_controller
        self.formView = formView
        self.dialog = dialog
        self.exception = None # Pour stocker une éventuelle exception
        
        
    def run(self):
        """Le code exécuté en arrière-plan. DOIT retourner True en cas de succès, False sinon."""
        QgsMessageLog.logMessage("Début de la tâche de génération du rapport.", "MonPlugin", Qgis.Info)
        try:
            total_steps = 2 # Nombre total d'étapes pour la progression
            current_step = 0

            # Étape 5: Construire le Rapport
            if self.isCanceled(): return False
            self.setProgress(current_step / total_steps * 100)
            QgsMessageLog.logMessage("Étape 5/5: Génération du document rapport...", "MonPlugin", Qgis.Info)
            self.rapport_controller.buildRapport(".docx")
            current_step += 1
            self.formView.setProgressBarValue(current_step + 4)

            # Étape finale: Garbage Collection
            if self.isCanceled(): return False
            QgsMessageLog.logMessage("Nettoyage mémoire...", "MonPlugin", Qgis.Info)
            current_step += 1
            self.formView.setProgressBarValue(current_step + 4)

            self.setProgress(100) # Tâche terminée

            QgsMessageLog.logMessage("Tâche de génération de rapport terminée avec succès.", "MonPlugin", Qgis.Success)
            return True # Succès
            

        except Exception as e:
            self.exception = e # Stocker l'exception pour l'afficher dans finished()
            QgsMessageLog.logMessage(f"Erreur pendant la tâche : {e}", "MonPlugin", Qgis.Critical)
            return False # Échec


    def finished(self, result):
        """Exécuté dans le thread principal après la fin de run()."""
        # Récupérer le bouton Valider de la dialogue

        if result:
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
