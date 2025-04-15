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
        
        # On regarde quel type de document est choisis :
        self.coucheManager.createSiteRetenu()
        print("rapport fait")
        
        
        
        
    def buildDocx(self):
        # Recuparation de l'emplacement du rapport et de son nom
        emplacement_rapport = self.configManager.getFromConfig("emplacement_rapport")[0]
        nom_rapport = self.configManager.getFromConfig("nom_rapport")[0]
        
        rapport_path = os.path.join(os.path.dirname(__file__), emplacement_rapport, nom_rapport)

        rapport = docx.Document()
        
        p = rapport.add_paragraph("Bonjour")
        
        rapport.save(rapport_path)

    def convertToPdf(self):
        fichier_docx_entree = "votre_document.docx"
        fichier_pdf_sortie = "votre_document.pdf" 
        #Todo : conversion du fichier docx créé en pdf