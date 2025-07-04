from .FormController import FormController
from ..model.CoucheModel import CoucheModel

import os
from qgis.core import QgsProject, QgsVectorLayer # type: ignore

class PluginController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.formController = FormController(dialog, couche_model_inst, config_model_inst, rapport_controller_inst)
        self.coucheModel = couche_model_inst
    
    
    
    def initPlugin(self):
        
        # Récupération de la couche
        emplacement_type_etendu = os.path.join(os.path.dirname(__file__), '..', 'couches', 'type_etendu.shp')
        nom_couche = "type_etendu"
        
        # Création de la couche
        vlayer = QgsVectorLayer(emplacement_type_etendu, nom_couche, "ogr")
        
        # Chargement de la couche dans le projet
        QgsProject.instance().addMapLayer(vlayer)
        
        # Lancement du formulaire
        try:
            self.formController.setupFormulaires()
        except Exception as e:
            print("Erreur lors du lancement du formulaire")
            print(e)
            raise
    
    