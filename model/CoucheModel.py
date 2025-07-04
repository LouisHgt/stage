import os

from .ConfigModel import ConfigModel
from qgis import processing  # type: ignore
from qgis.core import (  # type: ignore
    QgsFields, QgsVectorFileWriter, QgsField, QgsWkbTypes,
    QgsCoordinateReferenceSystem, QgsFeature, QgsVectorLayer,
    QgsProject, QgsGeometry, QgsPointXY, QgsFeatureRequest,
    QgsLayerTreeGroup
)
from qgis.PyQt.QtCore import QVariant  # type: ignore


class CoucheModel:

    def __init__(self):
        """Constructeur."""
        self.project = QgsProject.instance()
        self.configModel = ConfigModel()





    def getCoucheFromNom(self, nom_couche):
        """Récupère la couche QGIS depuis son nom."""
        couche = self.project.mapLayersByName(nom_couche)
        print(couche + nom_couche)
        if couche is not None:
            return couche[0]
        else:
            print('pas de couche avec ce nom : ' + nom_couche)
            return None








    def getCoucheFromFile(self, path_couche, nom_couche):
        """Charge une couche depuis un fichier, la copie en mémoire, libère le fichier et retourne la couche mémoire."""
        try:
            couche_fichier = QgsVectorLayer(path_couche, nom_couche, "ogr")
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
            couche_fichier = None
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






    def getFilteredNiveau(self, couche, liste_elt=[]):
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
                expression = ''
                i = 0
                for elt in liste_elt:
                    if isinstance(elt, str):
                        escaped_elt = elt.replace("'", "''")
                        expression += 'nv' + str(i) + ' = \'' + escaped_elt + '\' AND '
                        i += 1
                expression = self.remove_and(expression)
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
            return list(filtered_nv)





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
        tmp_path = os.path.join(os.path.dirname(__file__), '..', 'tmp')
        try:
            QgsVectorFileWriter.deleteShapeFile(tmp_path + "\\site_retenu.shp")
        except Exception as e:
            print(f"exception lors de la suppression des sites_retenus :{e}")
            raise
        if os.path.exists(tmp_path):
            for file_name in os.listdir(tmp_path):
                file_path = os.path.join(tmp_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression du fichier {file_path} : {e}")
                    raise
        else:
            try:
                os.makedirs(tmp_path)
            except OSError as e:
                print(f"Erreur lors de la création du dossier {tmp_path} : {e}")
                raise










    def createSiteRetenu(self, sites_retenus):
        """Crée la couche site_retenu à partir d'une liste de tuples -> sites_retenus"""


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
        fields.append(QgsField("nv1", QVariant.String, len=200))
        fields.append(QgsField("nv2", QVariant.String, len=200))
        fields.append(QgsField("nv3", QVariant.String, len=200))
        
        
        # Création d'une uri de base pour stocker la couche en memoire
        base_uri = "Point?crs=epsg:2154"
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
                
                # Ajout d'une geometrie nulle
                feature.setGeometry(QgsGeometry())
                
                feature_to_add.append(feature)
            
            # Insertion des données
            provider.addFeatures(feature_to_add)
            couche_site_retenu.updateExtents()
            
            self.writeLayer(couche_site_retenu, site_retenu_path)
                
        except Exception as e:
            print(f"Erreur lors de la creation de la couche site_retenu :{e}")
            raise

            
            
            
            
            
    
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