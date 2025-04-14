import docx
import os
from .configManager import configManager
from docx2pdf import convert

class rapportBuilder():
    def __init__(self):
        self.configManager = configManager()

    def buildRapport(self, fileType):
        
        # On vérifie que le type de fichier est docx ou pdf
        if(fileType != "docx" or fileType != "pdf"):
            print("Erreur : le type de fichier n'est pas reconnu (pdf ou docx)")
            return
        
        self.buildDocx()
        if(fileType == "pdf"):
            self.convertToPdf()
        
        
        
    def buildDocx(self):
        # Recuparation de l'emplacement du rapport et de son nom
        emplacement_rapport = self.configManager.getFromConfig("emplacement_rapport")[0]
        nom_rapport = self.configManager.getFromConfig("nom_rapport")[0]
        
        rapport_path = os.path.join(os.path.dirname(__file__), emplacement_rapport, nom_rapport)

        rapport = docx.Document()
        
        p = rapport.add_paragraph("Bonjour")
        
        rapport.save(rapport_path)

    def convertToPdf(self):
        fichier_docx_entree = "votre_document.docx"   # Remplacez par le chemin de votre fichier DOCX
        fichier_pdf_sortie = "votre_document.pdf"    # Remplacez par le nom souhaité pour le fichier PDF
        #Todo : conversion du fichier docx créé en pdf