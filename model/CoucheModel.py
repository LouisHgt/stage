import os

from .ConfigModel import ConfigModel
from qgis import processing # type: ignore
from qgis.core import ( # type: ignore
    QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsPointXY, QgsFeatureRequest,
    QgsLayerTreeGroup, QgsLayerTreeLayer
)
from qgis.PyQt.QtCore import QVariant # type: ignore

class CoucheModel():

    def __init__(self):
        """Constructeur."""
        self.project = QgsProject.instance()
        self.configModel = ConfigModel()

    def getCoucheFromNom(self, nom_couche):
        """Récupère la couche QGIS depuis son nom."""
        couche = self.project.mapLayersByName(nom_couche)
        if couche:
            return couche[0]
        else:
            print('pas de couche avec ce nom : ' + nom_couche)
            return None
    
    def getCoucheLocationFromNom(self, nom_couche):
        """Récupère l'emplacement physique (chemin) de la couche QGIS depuis son nom."""
        couche = self.getCoucheFromNom(nom_couche)
        if couche:
            # Récupérer l'URI de la couche
            uri = couche.dataProvider().dataSourceUri()
            # Si la couche est un fichier (comme un shapefile), extraire le chemin
            if "|" in uri:  # Vérifie si l'URI contient des paramètres (comme "|layerid=0")
                uri = uri.split("|")[0]  # Supprime les paramètres après "|"
            return uri
        else:
            print(f"La couche '{nom_couche}' est introuvable.")
            return None

    def getCoucheFromFile(self, path_couche, nom_couche):
        
        """
        Charge une couche depuis un fichier, la copie en mémoire,
        libère le fichier et retourne la couche mémoire.
        """
        
        try :
            
            # Recup fichier
            couche_fichier = QgsVectorLayer(path_couche, nom_couche, "ogr")
            
            
            # Copie dans la memoire
            uri_memoire = f"{QgsWkbTypes.displayString(couche_fichier.wkbType())}?crs={couche_fichier.crs().authid()}"
            couche_memoire = QgsVectorLayer(uri_memoire, nom_couche, "memory")
            
            provider_memoire = couche_memoire.dataProvider()
            provider_memoire.addAttributes(couche_fichier.fields().toList())
            couche_memoire.updateFields()
            
            features_a_copier = []
            for feature in couche_fichier.getFeatures():
                new_feature = QgsFeature(couche_memoire.fields())
                new_feature.setGeometry(feature.geometry())
                new_feature.setAttributes(feature.attributes())
                features_a_copier.append(new_feature)
                
            provider_memoire.addFeatures(features_a_copier)
            couche_memoire.updateExtents()
            
                   
            del couche_fichier
            
            return couche_memoire
            
        except Exception as e:
            print("Echec du chargement d'une couche : ")
            print(e)
            raise

            

    def getNbrAttributsCouche(self, couche):
        i = 0
        for field in couche.fields():
            i += 1
        
        return i
    
    def remove_and(self, text):
        """
        Supprime la sous-chaîne " AND " de la fin d'une chaîne, si elle est présente.
        """
        
        suffix = " AND "
        if text.endswith(suffix):
            # Retourne la chaîne jusqu'au début du suffixe trouvé
            return text[:-len(suffix)]
        else:
            # Retourne la chaîne originale si elle ne se termine pas par le suffixe
            return text
    
    def getFilteredNiveau(self, couche, liste_elt = []):
        
        
        # Récupération du niveau actuel
        nv = len(liste_elt)
        
        current_attribut = 'nv' + str(nv)
        filtered_nv = set()
        
        
        fields = couche.fields()
        attributs = []
        for field in fields.names():
            attributs.append(field)
        
        
        try:
            if nv != 0:
                # Construction de l'expression pour le filtre
                expression = ''
                i = 0
                
                
                for elt in liste_elt:
                    
                    if isinstance(elt, str):
                        escaped_elt = elt.replace("'", "''") # Remplacer ' par ''

                        expression += 'nv' + str(i) + ' = \'' + escaped_elt + '\' AND '
                        i +=1
                
                expression = self.remove_and(expression) # On supprimme le dernier AND
                
                request = QgsFeatureRequest().setFilterExpression(expression)
                request.setSubsetOfAttributes(attributs, fields)
                
                
                for f in couche.getFeatures(request):
                    filtered_nv.add(f[current_attribut])
                
                    
            else:


                request = QgsFeatureRequest().setSubsetOfAttributes(attributs, fields)
                for f in couche.getFeatures(request):
                    filtered_nv.add(f[current_attribut])
        
        except Exception as e:
            print(f"Une erreur s'est produite dans getFilteredNiveau : {e}")
            raise
        
        finally:
            return list(filtered_nv) # Conversion en liste
        
    def getSqlQuery(self, requete_path):
        try:

            with open(requete_path, 'r', encoding='utf-8') as f:
                sql_query = f.read()

        except FileNotFoundError:
            print("Erreur: Le fichier SQL '{sql_file_path_str}' n'a pas été trouvé.")
            raise
        except Exception as e:
            print("Erreur lors de la lecture du fichier SQL: {e}")
            raise
            
        return sql_query
        
    def clearTmpFolder(self):
        """Supprime tous les fichiers du dossier tmp."""
        tmp_path = os.path.join(os.path.dirname(__file__), '..',  'tmp')
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

    def get_group_layers(self, group):
        print('- group: ' + group.name())
        for child in group.children():
            if isinstance(child, QgsLayerTreeGroup):
                # Recursive call to get nested groups
                self.get_group_layers(child)
            else:
                print('  - layer: ' + child.name())
                
                
    def createStatusSensibilite(self, data):
        """Crée la couche shapefile de statut de sensibilité."""
        emplacement_couche = self.configModel.getFromConfig('emplacement_couche_status_sensibilite')
        nom_couche_config = self.configModel.getFromConfig('nom_couche_status_sensibilite')
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), '..',  emplacement_couche, nom_couche_shp)

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
            
            
            # root = self.project.layerTreeRoot()
            # for child in root.children():
            #     if isinstance(child, QgsLayerTreeGroup):
            #         self.get_group_layers(child)
                

        except Exception as e:
            print(f"ERREUR création couche {couche_path} : {e}")
            raise
        

    def createStatusScenario(self, data):
        """Crée la couche shapefile de statut de scénario."""
        emplacement_couche = self.configModel.getFromConfig('emplacement_couche_status_scenario')
        nom_couche_config = self.configModel.getFromConfig('nom_couche_status_scenario')
        nom_couche_base, _ = os.path.splitext(nom_couche_config)
        nom_couche_shp = nom_couche_base + '.shp'
        couche_path = os.path.join(os.path.dirname(__file__), '..',  emplacement_couche, nom_couche_shp)

        fields = QgsFields()
        fields.append(QgsField("nom_bassin", QVariant.String, "String"))
        fields.append(QgsField("indice_retour", QVariant.String, "String", 20))

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
                feature["indice_retour"] = indice_retour

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
            '..', 
            self.configModel.getFromConfig('emplacement_couche_site_retenu'),
            self.configModel.getFromConfig('nom_couche_site_retenu') + '.shp'
        )

        # Chemins d'entrée
        status_sentibilite_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            self.configModel.getFromConfig('emplacement_couche_status_sensibilite'),
            self.configModel.getFromConfig('nom_couche_status_sensibilite') + '.shp'
        )
        status_sentibilite_layer = QgsVectorLayer(status_sentibilite_path, "status_sentibilite_layer", "ogr")
        
        status_scenario_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            self.configModel.getFromConfig('emplacement_couche_status_scenario'),
            self.configModel.getFromConfig('nom_couche_status_scenario') + '.shp'
        )
        status_scenario_layer = QgsVectorLayer(status_scenario_path, "status_scenario_path", "ogr")

        
        
        
        # Vérification existence fichier source
        if not os.path.exists(status_sentibilite_path):
            raise FileNotFoundError(f"Fichier d'entrée pour SQL non trouvé: {status_sentibilite_path}")


        requete_path = os.path.join(os.path.dirname(__file__), '..', 'sql', self.configModel.getFromConfig('requete_formulaire'))
        
        requete = self.getSqlQuery(requete_path)
        

        try:
            # Exécution de l'algorithme Processing
            result = processing.run(
                "qgis:executesql",
                {
                    'INPUT_DATASOURCES': [
                        self.getCoucheLocationFromNom('SITES_BASES_SDIS filtre RDI') + '|layerid=0|subset="VISU_RDI" = \'1\'',
                        self.getCoucheLocationFromNom('type_etendu'),
                        status_sentibilite_layer,
                        status_scenario_layer
                    ],
                    'INPUT_QUERY': requete,
                    'INPUT_UID_FIELD': '',
                    'INPUT_GEOMETRY_FIELD': '',
                    'INPUT_GEOMETRY_TYPE': 0,
                    'INPUT_GEOMETRY_CRS': None,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )
            
            self.writeLayer(result['OUTPUT'], site_retenu_path)
            

        except Exception as e:
            print(f"ERREUR execution SQL sur {status_sentibilite_path} vers {site_retenu_path}: {e}")
            raise
        finally:
            del status_sentibilite_layer
            del status_scenario_layer
            del result
            
    def writeLayer(self, layer, emplacement_fichier):
        
        try:
            context = self.project.transformContext()
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.layerName = "site_retenu"
            options.encoding = "UTF-8"
            
            writer = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer,
                emplacement_fichier,
                context,
                options
            )
            del writer
        except Exception as e:
            print(e)
            raise
