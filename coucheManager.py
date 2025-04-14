from qgis.core import QgsProject

class coucheManager():
    
    def __init__(self, project):
        """Constructor"""
        self.project = project
    
    def getCoucheFromNom(self, nom_couche):
        """Recupere la couche Qgis depuis son nom."""
        couche = self.project.mapLayersByName(nom_couche)
        if couche:
            return couche[0]
        else:
            return None
    
    def createCouche(self, data):
        