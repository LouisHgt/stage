import os
from .configManager import configManager
from qgis import processing
# Ajout pour QgsGeometry et QgsPointXY si on teste avec une géométrie non nulle
from qgis.core import (
    QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsPointXY # Ajout QgsProject, QgsGeometry, QgsPointXY
)
from qgis.PyQt.QtCore import QVariant

class coucheManager():

    def __init__(self, project: QgsProject): # Typage explicite
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

        if os.path.exists(tmp_path):
            print(f"Nettoyage du dossier: {tmp_path}")
            for file_name in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f" Fichier supprimé : {file_path}")
                except Exception as e:
                    print(f" Erreur lors de la suppression du fichier {file_path} : {e}")
        else:
            print(f"Le dossier tmp {tmp_path} n'existe pas, création...")
            try:
                os.makedirs(tmp_path)
            except OSError as e:
                 print(f"Erreur lors de la création du dossier {tmp_path} : {e}")

    def createStatusSensibilite(self, data):
        """Crée une couche de statut de sensibilite."""
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0]
        nom_couche_config = self.configManager.getFromConfig('nom_couche_status_sensibilite')[0]
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche_shp)
        print(f"Préparation de la création de : {couche_path}")

        fields = QgsFields()
        fields.append(QgsField("id_type", QVariant.Int, "Integer"))
        fields.append(QgsField("etat_type", QVariant.Bool, "Boolean"))
        fields.append(QgsField("categorie", QVariant.String, "String", 10))

        crs = QgsCoordinateReferenceSystem("EPSG:4326")

        # Supprimer les fichiers existants avant de commencer
        print(f"Tentative de suppression des fichiers existants pour: {couche_path}")
        QgsVectorFileWriter.deleteShapeFile(couche_path) # Ne retourne rien, lance une exception si échoue?

        writer = None # Initialiser à None
        try:
            # --- Création du Writer ---
            writer = QgsVectorFileWriter(
                couche_path,
                "UTF-8",
                fields,
                QgsWkbTypes.Point,
                crs,
                driverName="ESRI Shapefile"
            )
            if writer.hasError() != QgsVectorFileWriter.NoError:
                 error_msg = f"Erreur lors de la création du writer pour {couche_path}: {writer.errorMessage()}"
                 print(error_msg)
                 raise Exception(error_msg)
            print("Writer créé avec succès.")

            # --- Ajout des entités ---
            feature = QgsFeature()
            feature.setFields(fields, True)
            # *** TEST: Mettre une géométrie non nulle pour forcer la création correcte SHP/SHX ***
            default_geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0))

            for id_key, etat_value in data.items():
                # feature.setGeometry(None) # Ancienne méthode
                feature.setGeometry(default_geom) # *** Nouvelle méthode (TEST) ***
                feature["id_type"] = id_key
                feature["etat_type"] = etat_value
                feature["categorie"] = "0"

                if not writer.addFeature(feature):
                    # Si une erreur survient ici, le fichier peut rester incomplet
                    print(f"ERREUR lors de l'ajout de l'entité {id_key} dans {couche_path}: {writer.errorMessage()}")
                    # On pourrait choisir de lever une exception ici pour arrêter
                    # raise Exception(f"Échec d'ajout feature {id_key}: {writer.errorMessage()}")
                # else: # Debug
                #    print(f"Entité {id_key} ajoutée.")

            print("Ajout des entités terminé.")

        except Exception as e:
            print(f"ERREUR GLOBALE lors de la création de la couche {couche_path} : {e}")
            # Lever à nouveau pour que l'appelant sache qu'il y a eu un problème
            raise
        finally:
            # --- Finalisation (ESSENTIEL) ---
            if writer is not None:
                print(f"Finalisation de l'écriture pour {couche_path} (del writer)...")
                del writer
                print("Writer finalisé.")
            else:
                print("Aucun writer à finaliser.")

            # Vérification post-écriture
            print("Vérification des fichiers après écriture:")
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                fpath = couche_path.replace('.shp', ext)
                print(f" {fpath} existe: {os.path.exists(fpath)}")


    def createStatusScenario(self, data):
        """Crée une couche de statut de scenario."""
        emplacement_couche = self.configManager.getFromConfig('emplacement_couche_status_scenario')[0]
        nom_couche_config = self.configManager.getFromConfig('nom_couche_status_scenario')[0]
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), emplacement_couche, nom_couche_shp)
        print(f"Préparation de la création de : {couche_path}")

        fields = QgsFields()
        fields.append(QgsField("nom_bassin", QVariant.String, "String"))
        fields.append(QgsField("indide_retour", QVariant.String, "String", 10))

        crs = QgsCoordinateReferenceSystem("EPSG:4326")

        print(f"Tentative de suppression des fichiers existants pour: {couche_path}")
        QgsVectorFileWriter.deleteShapeFile(couche_path)

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
            if writer.hasError() != QgsVectorFileWriter.NoError:
                 error_msg = f"Erreur lors de la création du writer pour {couche_path}: {writer.errorMessage()}"
                 print(error_msg)
                 raise Exception(error_msg)
            print("Writer créé avec succès.")

            feature = QgsFeature()
            feature.setFields(fields, True)
            default_geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0)) # Test géom non nulle

            for nom_bassin, indice_retour in data.items():
                feature.setGeometry(default_geom) # Test géom non nulle
                feature["nom_bassin"] = nom_bassin
                feature["indide_retour"] = indice_retour

                if not writer.addFeature(feature):
                    print(f"ERREUR lors de l'ajout de l'entité {nom_bassin} dans {couche_path}: {writer.errorMessage()}")

            print("Ajout des entités terminé.")

        except Exception as e:
            print(f"ERREUR GLOBALE lors de la création de la couche {couche_path} : {e}")
            raise
        finally:
            if writer is not None:
                print(f"Finalisation de l'écriture pour {couche_path} (del writer)...")
                del writer
                print("Writer finalisé.")
            else:
                print("Aucun writer à finaliser.")
            # Vérification post-écriture
            print("Vérification des fichiers après écriture:")
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                fpath = couche_path.replace('.shp', ext)
                print(f" {fpath} existe: {os.path.exists(fpath)}")


    def createSiteRetenu(self):
        """Crée la couche site_retenu via requête SQL."""

        # --- Chemins ---
        emplacement_couche_out = self.configManager.getFromConfig('emplacement_couche_site_retenu')[0]
        nom_couche_out_config = self.configManager.getFromConfig('nom_couche_site_retenu')[0]
        nom_couche_out_base, _ = os.path.splitext(nom_couche_out_config)
        nom_couche_out_shp = nom_couche_out_base + '.shp'
        output_path = os.path.join(os.path.dirname(__file__), emplacement_couche_out, nom_couche_out_shp)

        emplacement_couche_in = self.configManager.getFromConfig('emplacement_couche_status_sensibilite')[0]
        nom_couche_in_config = self.configManager.getFromConfig('nom_couche_status_sensibilite')[0]
        nom_couche_in_base, _ = os.path.splitext(nom_couche_in_config)
        input_layer_name_shp = nom_couche_in_base + ".shp"
        input_path = os.path.join(os.path.dirname(__file__), emplacement_couche_in, input_layer_name_shp)

        print(f"--- Création Site Retenu ---")
        print(f"Input path for SQL: {input_path}")
        print(f"Output path for SQL: {output_path}")


        # --- Requête SQL ---
        requete = "SELECT id_type, etat_type, categorie, geometry FROM input1"
        print(f"Exécution de la requête: {requete}")

        try:
            result = processing.run(
                "qgis:executesql",
                {
                    'INPUT_DATASOURCES': [input_path],
                    'INPUT_QUERY': requete,
                    'INPUT_UID_FIELD': '',
                    'INPUT_GEOMETRY_FIELD': '', # Laisser vide pour détection auto
                    'INPUT_GEOMETRY_TYPE': 0,   # 0 = Automatique
                    'INPUT_GEOMETRY_CRS': None, # None = Détection auto
                    'OUTPUT': output_path
                }
            )
            print(f"Algorithme processing.run terminé.")

        except Exception as e:
            print(f"ERREUR lors de l'exécution de processing.run('qgis:executesql') sur {input_path} : {e}")
            import traceback
            print(traceback.format_exc())
            raise