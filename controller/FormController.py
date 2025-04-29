from ..view.FormView import FormView
from .FormulaireTask import FormulaireTask

# --- Imports QGIS Core ---
from qgis.core import QgsApplication # type: ignore

class FormController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.dialog = dialog
        # Stocker les instances reçues
        self.coucheModel = couche_model_inst
        self.configModel = config_model_inst
        self.rapportController = rapport_controller_inst
        

        # Instancier la vue en passant les instances
        self.formView = FormView(dialog, self.coucheModel, self.configModel, self.rapportController)
        self.rapportController.setFormView(self.formView) # Passage de formView à rapportController
        self.rapportController.setDialog(self.dialog)
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
                
        boutonValider.setEnabled(False)
        boutonValider.setText('Traitement...')
        self.formView.setupProgressBar()

        # Récupérer les valeurs nécessaires du formulaire
        combo_values = self.formView.getComboBoxValues()
        checkbox_values = self.formView.getCheckboxValues()             
        # 3. Créer l'instance de la tâche
        task_description = "Génération du rapport DDTM"
        self.current_task = FormulaireTask(
            task_description,
            self.coucheModel,
            combo_values,
            checkbox_values,
            self.dialog
        )

        # Liaison de la tâche aux handlers
        self.current_task.progressChanged.connect(self.formView.handleUpdateProgressBar)
        self.current_task.task_finished.connect(self.rapportController.handleFormTaskFinished)
        # Ajouter la tâche au gestionnaire de tâches de QGIS
        QgsApplication.taskManager().addTask(self.current_task)
        
