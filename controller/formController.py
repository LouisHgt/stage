from ..view.formBuilder import formBuilder

class formController():
    def __init__(self, dialog):
        self.formBuilder = formBuilder(dialog)
    
    def setupFormulaires(self):
        """Configure les formulaires."""
        self.formBuilder.setupFormulaireScenario()
        self.formBuilder.setupFormulaireSensibilite()
        self.formBuilder.setupButtons()
        
    
    