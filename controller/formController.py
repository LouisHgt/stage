import os
from ..view.formView import formView
from ..model.coucheModel import coucheModel
from ..model import configModel

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

    
    def setupFormulaires(self):
        """Configure les formulaires."""
        self.formView.setupFormulaireScenario()
        self.formView.setupFormulaireSensibilite()
        self.formView.setupButtons(self)
        
    def pressed(self):
        """
            Affiche les données et les inscrit dans des couches
            Crée le rapport docx
            Ferme la boite de dialogue
        """
        
        # print(self.getComboBoxValues())
        # print(self.getCheckboxValues())
        
        self.coucheModel.clearTmpFolder()
        self.coucheModel.createStatusSensibilite(self.formView.getCheckboxValues())
        self.coucheModel.createStatusScenario(self.formView.getComboBoxValues())
        self.coucheModel.createSiteRetenu()
        
        self.rapportController.buildRapport(".docx")
        output = os.path.join(os.path.dirname(__file__), 'tmp')
        
        # Suppression des objets non referencés
        import gc
        gc.collect()
        
        
        self.dialog.accept()