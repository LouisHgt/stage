import os
import sqlite3

from .ConfigModel import ConfigModel
from qgis import processing # type: ignore
from qgis.core import ( # type: ignore
    QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsPointXY, QgsFeatureRequest,
    QgsLayerTreeGroup
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
        if couche is not None:
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
            if len(attributs) < nv:
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
        
        
        
        
        
    def upperCaseWithSpaces(self, string):
        """
            Prend un string en argument et renvoie en majuscule sans les -
        """

        return string.replace("-", " ").upper()
        
    
    
    
    
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






    def createSiteRetenu(self, sites_retenus):
        """Crée la couche site_retenu via requête SQL sur status_sensibilite."""

        # Couche de sortie
        site_retenu_path = os.path.join(
            os.path.dirname(__file__),
            '..', 
            self.configModel.getFromConfig('emplacement_couche_site_retenu'),
            self.configModel.getFromConfig('nom_couche_site_retenu') + '.shp'
        )
        
        
        # Création de la couche
        # Définir les champs
        fields = QgsFields()
        fields.append(QgsField("nv0", QVariant.String, len=50))
        fields.append(QgsField("nv1", QVariant.String, len=100))
        fields.append(QgsField("nv2", QVariant.String, len=50))
        fields.append(QgsField("nv3", QVariant.String, len=100))
        
        
        # Création d'une uri de base opur stocker la couche en memoire
        base_uri = "NoGeometry?crs=epsg:2154"
        nom_layer = self.configModel.getFromConfig('nom_couche_site_retenu')
        
        
        # Création de la couche en memoire
        try:
            couche_site_retenu = QgsVectorLayer(base_uri, nom_layer, "memory")
            
            
            
            provider = couche_site_retenu.dataProvider()
            # 2. Ajouter les champs à partir de votre objet QgsFields existant
            # Note: addAttributes attend une liste de QgsField, pas un QgsFields.
            # On peut convertir QgsFields en liste de QgsField.
            provider.addAttributes([fields.field(i) for i in range(fields.count())])
            
            couche_site_retenu.updateFields()
            
            
            # Ajout des données dans feature_to_add
            feature_to_add = []
            for site_tuple in sites_retenus:
                feature = QgsFeature(couche_site_retenu.fields())
                feature.setAttributes(list(site_tuple))
                
                feature_to_add.append(feature)
            
            # Insertion des données
            provider.addFeatures(feature_to_add)
            couche_site_retenu.updateExtents()
            
            self.writeLayer(couche_site_retenu, site_retenu_path)
                
        except Exception as e:
            print(f"Erreur lors de la creation de la couche site_retenu :{e}")
            raise

            
            
            
            
            
            
            
    def createSites(self):
        # Couche de sortie
        sites_tries = os.path.join(
            os.path.dirname(__file__),
            '..', 
            self.configModel.getFromConfig('emplacement_couche_site_tries'),
            self.configModel.getFromConfig('nom_couche_sites_tries') + '.shp'
        )
        
        # Couches d'entrée
        sites_base_RDI = self.getCoucheLocationFromNom('SITES_BASES_SDIS filtre RDI') + '|layerid=0|subset="VISU_RDI" = \'1\''
        
        
        # Récupération de la requete
        requete_path = os.path.join(os.path.dirname(__file__), '..', 'sql', self.configModel.getFromConfig('requete_sites'))
        requete = self.getSqlQuery(requete_path)
        
        result = None
        
        # Execution de la requete
        try:
            # Exécution de l'algorithme Processing
            result = processing.run(
                "qgis:executesql",
                {
                    'INPUT_DATASOURCES': [
                        sites_base_RDI
                    ],
                    'INPUT_QUERY': requete,
                    'INPUT_UID_FIELD': '',
                    'INPUT_GEOMETRY_FIELD': '',
                    'INPUT_GEOMETRY_TYPE': 0,
                    'INPUT_GEOMETRY_CRS': None,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
            )
                        
            # On érit la couche en fichier et on l'ajoute au projet
            self.writeLayer(result['OUTPUT'], sites_tries)
            
            print(sites_tries)
            print(self.configModel.getFromConfig('nom_couche_sites_tries'))
            
            layer_from_file = QgsVectorLayer(
                sites_tries,
                self.configModel.getFromConfig('nom_couche_sites_tries'),
                "ogr"
            )
            self.project.addMapLayer(layer_from_file, False)


        except Exception as e:
            print(f"ERREUR execution SQL sur {sites_base_RDI} vers {sites_tries}: {e}")
            raise
        finally:
            del sites_base_RDI
            del sites_tries
            del result
    
    
    
    
    
    def save_bassins(self, couche_sauvegarde, data):
        # Ouvre la couche, modifie tous les champs
        # avec les valeurs des combobox et la sauvegarde
        couche_sauvegarde.startEditing()
                
        for feature in couche_sauvegarde.getFeatures():
            
            value = data.get(feature['LIB'])
                        
            if data.get(feature['LIB']):
                feature['OCCUR'] = value
            else:
                feature['OCCUR'] = 0
                
            couche_sauvegarde.updateFeature(feature)
        
        # On annule les changements si il y a une erreur
        if not couche_sauvegarde.commitChanges():
            print("Erreur de sauvegarde")
            couche_sauvegarde.rollBack()
        # Sinon on refresh la couche
        else:
            print("Sauvegarde reussie")
        
    
    
    
    
    def writeLayer(self, layer, emplacement_fichier):
        
        try:
            context = self.project.transformContext()
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.layerName = "site_retenu"
            options.encoding = "UTF-8"
            
            QgsVectorFileWriter.writeAsVectorFormatV3(
                layer,
                emplacement_fichier,
                context,
                options
            )
        except Exception as e:
            print(e)
            raise


    
    
    def get_sites_from_couche(self, nom_couche):
        """
        Récupère la couche
        Récupère les index des attributs qu'on va récupérer (plus rapide)
        Parcours la couche pour stocker les données dans une liste de tuples 
        (lisible par la requete qui stockera les données en table bd)
        """
        
        
        # Récupération de la couche
        couche = self.getCoucheFromNom(nom_couche)
        
        # Récupération des index
        fields = couche.fields()
        
        idx_nom_site = fields.indexFromName("NOM")
        idx_type_site = fields.indexFromName("TYPE")
        idx_commune_site = fields.indexFromName("COMMUNE")
        idx_sect_inond_site = fields.indexFromName("SECT_INOND")
        idx_freq_inond_site = fields.indexFromName("FREQ_INOND")
        
        data = []
        
        if couche and couche.isValid() and isinstance(couche, QgsVectorLayer):
            for feature in couche.getFeatures():
                
                # Récupération des données
                nom_site = feature.attribute(idx_nom_site)
                type_site = feature.attribute(idx_type_site)
                nom_commune_site = feature.attribute(idx_commune_site)
                sect_inond_site = feature.attribute(idx_sect_inond_site)
                freq_inond_site = feature.attribute(idx_freq_inond_site)
                
                
                # Stockage dans la liste de tuples
                data.append((nom_site, type_site, nom_commune_site, sect_inond_site, freq_inond_site, feature.geometry().asWkt()))
        
        
        return data