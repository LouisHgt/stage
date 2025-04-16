import docx
import os
from .configManager import configManager
from .coucheManager import coucheManager
from docx2pdf import convert

class rapportBuilder():
    def __init__(self, project):
        self.configManager = configManager()
        self.coucheManager = coucheManager(project)

    def buildRapport(self, fileType1, fileType2 = None):
        """Recupere les données d'entrée de la table 'site retenu' et crée un docx avec

        Args:
            Prend entre 1 et deux types de documents de sortie
        """
        
        # Recuparation de l'emplacement du rapport et de son nom
        emplacement_rapport = self.configManager.getFromConfig("emplacement_rapport")[0]
        nom_rapport = self.configManager.getFromConfig("nom_rapport")[0]
        
        rapport_path = os.path.join(os.path.dirname(__file__), emplacement_rapport, nom_rapport)

        rapport = docx.Document()
        # On regarde quel type de document est choisis :
        
        liste = []
        
        rapport = self.buildDocx(rapport, liste)
        
        print("rapport fait")
        
        
        
        
    def buildDocx(self, document,  liste_elements, niveau):
        """Fonction recursive qui parcours pour un elt d'un niveau les elt du niveau +1"""
        if not liste_elements:
            return document
        
        for elt in liste_elements:
            
            document.addHeading(elt, niveau)
            
            # On rappelle la fonction pour parcourir la sous liste
            document = self.buildDocx(document, liste_elements[elt], niveau + 1)
        
        return document

    def convertToPdf(self):
        fichier_docx_entree = "votre_document.docx"
        fichier_pdf_sortie = "votre_document.pdf" 
        #Todo : conversion du fichier docx créé en pdf