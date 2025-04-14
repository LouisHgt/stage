import os
from .configManager import configManager
from qgis.core import QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsFeature # type: ignore
from qgis.PyQt.QtCore import QVariant # type: ignore

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
        nom_couche = self.configManager.getFromConfig('nom_couche_status_sensibilite')[0]
        
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche)
        


                
        # Creation de la couche 
        
        fields = QgsFields()
        
        fields.append(QgsField("id_type", QVariant.Int, "Integer")) # id du type de site correspondant à la table nom_couche_type du fichier config
        fields.append(QgsField("etat_type", QVariant.Bool, "Boolean"))      # Selectionné ou pas
        fields.append(QgsField("categorie", QVariant.String, "String", 10)) # Ajout de la colonne categorie (String de longueur 10 par ex.)
        
        try:
            writer = QgsVectorFileWriter(
                couche_path,                  # Chemin du fichier de sortie
                "UTF-8",                      # Encodage du fichier
                fields,                       # Structure des champs définis ci-dessus
                QgsWkbTypes.NoGeometry,       # Important: Pas de géométrie
                QgsCoordinateReferenceSystem(),
                driverName="ESRI Shapefile"   # Driver pour créer le .dbf
            )
            
            feature = QgsFeature()
            feature.setFields(fields, True) # Initialiser la structure de l'entité
            
            for id_key, etat_value in data.items():
                
                # Assigner les valeurs aux attributs de l'entité
                feature["id_type"] = id_key
                feature["etat_type"] = etat_value
                # !! A CHANGER !! 
                feature["categorie"] = "0" # 0 par défaut car on ne connait pas encore la categorie avec le formulaire la categorie
                
                writer.addFeature(feature)
                
            # Ecrire dans le fichier de sortie
            del writer
            print(f"Fichier {couche_path} créé avec succès.")

        except Exception as e:
            print(f"Erreur lors de la création de la couche : {e}")
            raise
                
        
    def createStatusScenario(self, data):
        print(data)