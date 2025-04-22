import os
from ..view.formView import formView
from ..model.coucheModel import coucheModel
from ..model import configModel

class formController():
    def __init__(self, dialog):
        self.coucheModel = coucheModel()
        self.configModel = configModel()
        self.formView = formView(dialog, coucheModel, configModel)

    
    def setupFormulaires(self):
        """Configure les formulaires."""
        self.formView.setupFormulaireScenario()
        self.formView.setupFormulaireSensibilite()
        self.formView.setupButtons()
        
    def pressed(self):
        """
            Affiche les données et les inscrit dans des couches
            Crée le rapport docx
            Ferme la boite de dialogue
        """
        
        # print(self.getComboBoxValues())
        # print(self.getCheckboxValues())
        
        self.coucheModel.clearTmpFolder()
        self.coucheModel.createStatusSensibilite(self.getCheckboxValues())
        self.coucheModel.createStatusScenario(self.getComboBoxValues())
        self.coucheModel.createSiteRetenu()
        
        self.rapportController.buildRapport(".docx")
        output = os.path.join(os.path.dirname(__file__), 'tmp')
        
        # Suppression des objets non referencés
        import gc
        gc.collect()
        
        
        self.dialog.accept()