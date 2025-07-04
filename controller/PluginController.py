from .FormController import FormController
from ..model.CoucheModel import CoucheModel

import os
from qgis.core import QgsProject # type: ignore

class PluginController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.formController = FormController(dialog, couche_model_inst, config_model_inst, rapport_controller_inst)
        self.coucheModel = couche_model_inst
    
    
    
    def initPlugin(self):
        
        # Récupération de la couche
        emplacement_type_etendu = os.path.join(os.path.dirname(__file__), '..', 'couches')
        nom_couche = "type_etendu.shp"
        
        # Création de la couche
        vlayer = self.coucheModel.getCoucheFromFile(emplacement_type_etendu, nom_couche)
        
        # Chargement de la couche dans le projet
        QgsProject.instance().addMapLayer(vlayer)
        print("la couche est chargée")
        
        # Lancement du formulaire
        try:
            self.formController.setupFormulaires()
        except Exception as e:
            print("Erreur lors du lancement du formulaire")
            print(e)
            raise
    
    