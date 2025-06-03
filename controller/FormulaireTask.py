from qgis.core import QgsTask, QgsMessageLog, Qgis # type: ignore
from qgis.PyQt import QtWidgets # type: ignore
from qgis.PyQt.QtCore import pyqtSignal # type: ignore

from ..model.DataBaseModel import DataBaseModel

class FormulaireTask(QgsTask):
    """Tâche QGIS pour générer le rapport en arrière-plan."""

    # Signal de fin de tache
    task_finished = pyqtSignal(bool)   
     
    def __init__(self, description, couche_model, combo_values, checkbox_values, dialog_reference):
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
        self.combo_values = combo_values
        self.checkbox_values = checkbox_values
        self.dialog = dialog_reference # Garde une référence à la dialog
        self.exception = None # Pour stocker une éventuelle exception

        
        
    def run(self):
        """Le code exécuté en arrière-plan. DOIT retourner True en cas de succès, False sinon."""
        QgsMessageLog.logMessage("Début de la tâche de recuperation des données selon le formulaire.", "MonPlugin", Qgis.Info)
        try:
            total_steps = 9 # Nombre total d'étapes pour la progression
            current_step = 0
            self.setProgress(current_step / total_steps * 100)

            # Étape 1: Nettoyer Tmp
            if self.isCanceled(): return False
            self.couche_model.clearTmpFolder() # Action de l'etape
            current_step += 1
            self.setProgress(current_step / total_steps * 100)






            # Étape 2: Initialisation de la bd
            if self.isCanceled(): return False
            dataBaseModel = DataBaseModel(self.couche_model)
            current_step += 1
            self.setProgress(current_step / total_steps * 100)
            
            
            
            
            
            
            # Étape 3: Création de la table type etendus
            if self.isCanceled(): return False
            dataBaseModel.create_table_type_etendu()
            current_step += 1
            self.setProgress(current_step / total_steps * 100)

            
            
            
            
            
            
            # Étape 4: Création de la table status_scenario
            if self.isCanceled(): return False
            dataBaseModel.create_table_status_scenario(self.combo_values)
            current_step += 1
            self.setProgress(current_step / total_steps * 100)
            
            
            
            
            
            
            
            # Étape 5: Création de la table status_sensibilite
            if self.isCanceled(): return False
            dataBaseModel.create_table_status_sensibilite(self.checkbox_values)
            current_step += 1
            self.setProgress(current_step / total_steps * 100)

            
            
            
            
            
            
            # Étape 6: Récupération des sites dans la couche sites base sdis et conversion en types pythons
            data = dataBaseModel.convertDataTypes(self.couche_model.get_sites_from_couche('SITES_BASES_SDIS filtre RDI'))
            # Création de la table sites_base_sdis_filtre_rdi
            dataBaseModel.create_table_sites("sites_bases_sdis_filtre", data)
            del data # On supprime data pour libérer de la mémoire
            current_step += 1
            self.setProgress(current_step / total_steps * 100)





            # Étape 7: Création de la table sites
            if self.isCanceled(): return False
            # Récupération de l'ensemble des sites
            data = dataBaseModel.get_sites(["sites_bases_sdis_filtre"])
            dataBaseModel.create_table_sites("sites", data)
            del data # On supprime data pour libérer de la mémoire
            current_step += 1
            self.setProgress(current_step / total_steps * 100)

            
            
            
            
            


            # Étape 8: Requete finale des sites retenus
            if self.isCanceled(): return False
            sites_retenus = dataBaseModel.get_sites_retenus()
            current_step += 1
            self.setProgress(current_step / total_steps * 100)



            # Étape 9: Creation du fichier site_retenu
            if self.isCanceled(): return False
            self.couche_model.createSiteRetenu(sites_retenus)
            current_step += 1
            self.setProgress(current_step / total_steps * 100)


            return True
            
            

        except Exception as e:
            self.exception = e # Stocker l'exception pour l'afficher dans finished()
            QgsMessageLog.logMessage(f"Erreur pendant la tâche : {e}", "MonPlugin", Qgis.Critical)
            return False # Échec


    def finished(self, result):
        """Exécuté dans le thread principal après la fin de run()."""
        # Récupérer le bouton Valider de la dialogue

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
