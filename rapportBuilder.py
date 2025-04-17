
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
        # # On regarde quel type de document est choisis :
        
        niveau = 0
        self.buildDocx(self.coucheManager.getColoneWithoutDoubles(str(niveau)), 0)
        
        self.rapport.save(rapport_path)
        del self.rapport
        print("rapport fait")

        
        
        
        
    def buildDocx(self, liste_elements, niveau):
        """Fonction recursive qui parcours pour un elt d'un niveau les elt du niveau +1"""
        if not liste_elements:
            return
        
        for elt in liste_elements:
            
            print(elt, niveau)
            self.rapport.add_heading(elt, niveau)
            
            nv_liste = self.coucheManager.getColoneWithoutDoubles(str(niveau + 1), elt)
        
            #On vérifie si on est à une feuille 
            if not nv_liste:
                break
            # On rappelle la fonction pour parcourir la sous liste
            self.buildDocx(nv_liste, niveau + 1)
        

    def convertToPdf(self):
        fichier_docx_entree = "votre_document.docx"
        fichier_pdf_sortie = "votre_document.pdf" 
        #Todo : conversion du fichier docx créé en pdf