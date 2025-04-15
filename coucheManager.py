import os
from .configManager import configManager
from qgis import processing # type: ignore
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
    
    def clearTmpFolder(self):
        """Supprime tous les fichiers du dossier tmp."""
        tmp_path = os.path.join(os.path.dirname(__file__), 'tmp')
        
        # Vérifie si le dossier tmp existe
        if os.path.exists(tmp_path):
            for file_name in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, file_name)
                try:
                    if os.path.isfile(file_path):  # Vérifie si c'est un fichier
                        os.remove(file_path)  # Supprime le fichier
                        print(f"Fichier supprimé : {file_path}")
                except Exception as e:
                    print(f"Erreur lors de la suppression du fichier {file_path} : {e}")
        else:
            print(f"Le dossier {tmp_path} n'existe pas.")
            
    
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
                feature["categorie"] = "0" # 0 par défaut car on ne connait pas encore la categorie avec le formulaire
                
                writer.addFeature(feature)
                
            # Ecrire dans le fichier de sortie
            del writer
            print("Fichier " + couche_path + " créé avec succès.")

        except Exception as e:
            print("Erreur lors de la création de la couche : {e}")
            raise
                
        
    def createStatusScenario(self, data):
        """Crée une couche de statut de scenario.
        
        Elle stocke pour chaque bassin versant son indice de retour annuel.
        
        Elle recoit des données du type : 
        {
            'BEVERA': 'Q10',
            'LITTORAL ESTEREL': 'Qex',
            'CAGNE': 'AZI'
        }
        """
        
        # Construction du path de la couche à créer
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_scenario')[0]
        nom_couche = self.configManager.getFromConfig('nom_couche_status_scenario')[0]
        
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche)
        
        
        # Creation de la couche 
        fields = QgsFields()
        
        fields.append(QgsField("nom_bassin", QVariant.String, "String")) # Nom du bassin et identifiant
        fields.append(QgsField("indide_retour", QVariant.String, "String", 10)) # Indice de retour associé
        
        try:
            writer = writer = QgsVectorFileWriter(
                couche_path,                  # Chemin du fichier de sortie
                "UTF-8",                      # Encodage du fichier
                fields,                       # Structure des champs définis ci-dessus
                QgsWkbTypes.NoGeometry,       # Important: Pas de géométrie
                QgsCoordinateReferenceSystem(),
                driverName="ESRI Shapefile"   # Driver pour créer le .dbf
            )
            
            feature = QgsFeature()
            feature.setFields(fields, True) # Initialiser la structure de l'entité
            
            for nom_bassin, indice_retour in data.items():
                
                # Assigner les valeurs aux attributs de l'entité
                feature["nom_bassin"] = nom_bassin
                feature["indide_retour"] = indice_retour
                                
                writer.addFeature(feature)
                
            # Ecrire dans le fichier de sortie
            del writer
            print("Fichier " + couche_path + " créé avec succès.")
            
        except Exception as e:
            print("Erreur lors de la création de la couche : {e}")
            raise
        
        
    def createSiteRetenu(self):
        
        # Construction du path de la couche à créer
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_site_retenu')[0]
        nom_couche = self.configManager.getFromConfig('nom_couche_site_retenu')[0]
        
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche)
        
        emplacement_couche_status_sensibilite = self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0]
        nom_couche_status_sensibilite = self.configManager.getFromConfig('nom_couche_status_sensibilite')[0] + ".dbf"
        input_path = os.path.join(os.path.dirname(__file__), emplacement_couche_status_sensibilite, nom_couche_status_sensibilite)
        
        print(input_path)
        # Creation de la couche avec la requete SQL
        requete = "SELECT * FROM input1"
        
        processing.runAndLoadResults(
            "qgis:executesql",
            {
                'INPUT_DATASOURCES': [input_path],  # Fichier d'entrée
                'INPUT_QUERY': requete,            # Requête SQL
                'INPUT_UID_FIELD': '',             # Aucun champ UID
                'INPUT_GEOMETRY_FIELD': '',        # Pas de champ géométrique
                'INPUT_GEOMETRY_TYPE': 0,          # Pas de géométrie
                'INPUT_GEOMETRY_CRS': None,        # Pas de CRS
                'OUTPUT': couche_path              # Chemin de sortie
            }
        )
        
        
        