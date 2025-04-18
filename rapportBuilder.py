
import os
from .configManager import configManager
from .coucheManager import coucheManager
from docx2pdf import convert

class rapportBuilder():
    def __init__(self, coucheManager):
        self.configManager = configManager()
        self.coucheManager = coucheManager

    def buildRapport(self, fileType1):
        # On importe docx dans la methode pour eviter les conflits avec le garbage collector
        import docx
        """Recupere les données d'entrée de la table 'site retenu' et crée un docx avec

        Args:
            Prend entre 1 et deux types de documents de sortie
        """
        
        # Recuparation de l'emplacement du rapport et de son nom
        emplacement_rapport = self.configManager.getFromConfig("emplacement_rapport")[0]
        nom_rapport = self.configManager.getFromConfig("nom_rapport")[0]
        
        rapport_path = os.path.join(os.path.dirname(__file__), emplacement_rapport, nom_rapport) + fileType1

        self.rapport = docx.Document()
        
        # Recuperation de la couche site_retenu
        emplacement_couche_site_retenu = self.configManager.getFromConfig('emplacement_couche_site_retenu')[0]
        nom_couche_site_retenu = self.configManager.getFromConfig('nom_couche_site_retenu')[0]
        path_site_retenu = os.path.join(os.path.dirname(__file__), emplacement_couche_site_retenu, nom_couche_site_retenu) + ".shp"
        couche = self.coucheManager.getCoucheFromFile(path_site_retenu, "site_retenu")

        
        
        self.niveau = self.coucheManager.getNbrAttributsCouche(couche)
        self.list = [] # Liste dans laquelle on stocke les elements servants au filtre
        self.buildDocx(couche, self.coucheManager.getFilteredNiveau(couche))
        
        
        self.rapport.save(rapport_path)
        del self.rapport
        print("rapport ecrit")

        
        
        
        
    def buildDocx(self, couche,  liste_elements):
        """Fonction recursive qui parcours pour un elt d'un niveau les elt du niveau +1"""
        # Condition d'arret
        if len(self.list) >= self.niveau - 1:
            for elt in liste_elements:
                self.rapport.add_heading(elt, 1)
            return
        
        for elt in liste_elements:
            
                        
            self.list.append(elt)
            self.rapport.add_heading(elt, 1)
            
            
            
            # On filtre
            nv_liste = self.coucheManager.getFilteredNiveau(couche, self.list)
            # On rappelle avec la nouvelle liste
            self.buildDocx(couche, nv_liste)
            self.list.pop()
            

            
            
        

    def convertToPdf(self):
        fichier_docx_entree = "votre_document.docx"
        fichier_pdf_sortie = "votre_document.pdf" 
        #Todo : conversion du fichier docx créé en pdf