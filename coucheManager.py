import os
from .configManager import configManager
from qgis.core import QgsFields, QgsVectorFileWriter, QgsField, QVariant

class coucheManager():
    
    def __init__(self, project):
        """Constructor"""
        self.project = project
        self.configManager = configManager()
        
    
    def getCoucheFromNom(self, nom_couche):
        """Recupere la couche Qgis depuis son nom."""
        couche = self.project.mapLayersByName(nom_couche)
        if couche:
            return couche[0]
        else:
            return None
    
    def createStatusSensibilite(self, data):
        """Crée une couche de statut de sensibilite.
        
        Elle stocke pour chaque type de site si il est selectionné ou pas.
        
        Elle recoit des données du type : 
        {
            1: True,
            2: False,
            3: True
        }
        """
        
        
        # Construction du path de la couche à créer
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0]
        nom_couche = configManager.getFromConfig('nom_couche_status_sensibilite')[0]
        
        couche_path = os.path.join(emplacement_couche, nom_couche)
        
        layer_name = "status_sensibilite"
        
        # Creation de la couche 
        
        fields = QgsFields()
        
        fields.append(QgsField("id_type", QVariant.Int, "Integer")) # id du type de site correspondant à la table nom_couche_type du fichier config
        fields.append(QgsField("etat_type", QVariant.Bool, "Boolean"))      # Selectionné ou pas
        fields.append(QgsField("categorie", QVariant.String, "String", 10)) # Ajout de la colonne categorie (String de longueur 10 par ex.)
        
        