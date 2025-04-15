import os

from .configManager import configManager
from qgis import processing # type: ignore
from qgis.core import ( # type: ignore
    QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsPointXY
)
from qgis.PyQt.QtCore import QVariant # type: ignore

class coucheManager():

    def __init__(self, project: QgsProject):
        """Constructeur."""
        self.project = project
        self.configManager = configManager()

    def getCoucheFromNom(self, nom_couche):
        """Récupère la couche QGIS depuis son nom."""
        couche = self.project.mapLayersByName(nom_couche)
        if couche:
            return couche[0]
        else:
            return None

    def clearTmpFolder(self):
        """Supprime tous les fichiers du dossier tmp."""
        tmp_path = os.path.join(os.path.dirname(__file__), 'tmp')
        if os.path.exists(tmp_path):
            for file_name in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f" Erreur lors de la suppression du fichier {file_path} : {e}")
        else:
            # Créer le dossier si nécessaire
            try:
                os.makedirs(tmp_path)
            except OSError as e:
                 print(f"Erreur lors de la création du dossier {tmp_path} : {e}")

    def createStatusSensibilite(self, data):
        """Crée la couche shapefile de statut de sensibilité."""
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0]
        nom_couche_config = self.configManager.getFromConfig('nom_couche_status_sensibilite')[0]
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche_shp)

        fields = QgsFields()
        fields.append(QgsField("id_type", QVariant.Int, "Integer"))
        fields.append(QgsField("etat_type", QVariant.Bool, "Boolean"))
        fields.append(QgsField("categorie", QVariant.String, "String", 10))

        crs = QgsCoordinateReferenceSystem("EPSG:4326")

        # Supprimer les fichiers shapefile existants pour éviter conflit
        QgsVectorFileWriter.deleteShapeFile(couche_path)

        writer = None
        try:
            writer = QgsVectorFileWriter(
                couche_path,
                "UTF-8",
                fields,
                QgsWkbTypes.Point, # Nécessaire pour format SHP
                crs,
                driverName="ESRI Shapefile"
            )


            feature = QgsFeature()
            feature.setFields(fields, True)
            default_geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0)) # Géométrie par défaut

            for id_key, etat_value in data.items():
                feature.setGeometry(default_geom)
                feature["id_type"] = id_key
                feature["etat_type"] = etat_value
                feature["categorie"] = "0" # TODO: A adapter si nécessaire
                
                writer.addFeature(feature)
                
            del writer # Ferme et finalise le fichier

        except Exception as e:
            print(f"ERREUR création couche {couche_path} : {e}")
            raise
        

    def createStatusScenario(self, data):
        """Crée la couche shapefile de statut de scénario."""
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_scenario')[0]
        nom_couche_config = self.configManager.getFromConfig('nom_couche_status_scenario')[0]
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche_shp)

        fields = QgsFields()
        fields.append(QgsField("nom_bassin", QVariant.String, "String"))
        fields.append(QgsField("indide_retour", QVariant.String, "String", 10))

        crs = QgsCoordinateReferenceSystem("EPSG:4326")

        QgsVectorFileWriter.deleteShapeFile(couche_path) # Nettoyage préalable

        writer = None
        try:
            writer = QgsVectorFileWriter(
                couche_path,
                "UTF-8",
                fields,
                QgsWkbTypes.Point,
                crs,
                driverName="ESRI Shapefile"
            )

            feature = QgsFeature()
            feature.setFields(fields, True)
            default_geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0))

            for nom_bassin, indice_retour in data.items():
                feature.setGeometry(default_geom)
                feature["nom_bassin"] = nom_bassin
                feature["indide_retour"] = indice_retour

                writer.addFeature(feature)
                
            del writer # Ferme et finalise le fichier

        except Exception as e:
            print(f"ERREUR création couche {couche_path} : {e}")
            raise


    def createSiteRetenu(self):
        """Crée la couche site_retenu via requête SQL sur status_sensibilite."""

        # Chemin de sortie
        site_retenu_path = os.path.join(
            os.path.dirname(__file__),
            self.configManager.getFromConfig('emplacement_couche_site_retenu')[0],
            self.configManager.getFromConfig('nom_couche_site_retenu')[0] + '.shp'
        )

        # Chemins d'entrée
        status_sentibilite_path = os.path.join(
            os.path.dirname(__file__),
            self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0],
            self.configManager.getFromConfig('nom_couche_status_sensibilite')[0] + '.shp'
        )
        
        status_scenario_path = os.path.join(
            os.path.dirname(__file__),
            self.configManager.getFromConfig('emplacement_couche_status_scenario')[0],
            self.configManager.getFromConfig('nom_couche_status_scenario')[0] + '.shp'
        )
        
        
        
        
        # Vérification existence fichier source
        if not os.path.exists(status_sentibilite_path):
            raise FileNotFoundError(f"Fichier d'entrée pour SQL non trouvé: {status_sentibilite_path}")

        # Requête SQL incluant la géométrie (nécessaire pour sortie SHP)
        requete = self.configManager.getFromConfig('requete')
        print(requete)


        try:
            # Exécution de l'algorithme Processing
            result = processing.run(
                "qgis:executesql",
                {
                    'INPUT_DATASOURCES': [status_sentibilite_path],
                    'INPUT_QUERY': requete,
                    'INPUT_UID_FIELD': '',
                    'INPUT_GEOMETRY_FIELD': '',
                    'INPUT_GEOMETRY_TYPE': 0,
                    'INPUT_GEOMETRY_CRS': None,
                    'OUTPUT': site_retenu_path
                }
            )

        except Exception as e:
            print(f"ERREUR execution SQL sur {status_sentibilite_path} vers {site_retenu_path}: {e}")
            raise