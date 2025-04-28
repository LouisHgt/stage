import os
import docx
import subprocess

from .docxBuilder import docxBuilder

class rapportController():
    def __init__(self, config_model_inst, couche_model_inst):
        self.configModel = config_model_inst
        self.coucheModel = couche_model_inst
        self.docxBuilder = docxBuilder()
        
    def setFormView(self, formView):
        self.formView = formView
        
    def setDialog(self, dialog):
        self.dialog = dialog
        
    def buildRapport(self):
        # On importe docx dans la methode pour eviter les conflits avec le garbage collector
        
        """
            Recupere les données d'entrée de la table 'site retenu' et crée un docx avec
        """
        
        # Recuparation de l'emplacement du rapport et de son nom
        emplacement_rapport = self.configModel.getFromConfig("emplacement_rapport")
        nom_rapport = self.configModel.getFromConfig("nom_rapport")
        
        rapport_path = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport, nom_rapport) + ".docx"

        # Instaciation du doc
        self.docxBuilder.initDoc()
        self.docxBuilder.initDoc()
        

        
        # Recuperation de la couche site_retenu
        emplacement_couche_site_retenu = self.configModel.getFromConfig('emplacement_couche_site_retenu')
        nom_couche_site_retenu = self.configModel.getFromConfig('nom_couche_site_retenu')
        path_site_retenu = os.path.join(os.path.dirname(__file__), '..', emplacement_couche_site_retenu, nom_couche_site_retenu) + ".shp"
        couche = self.coucheModel.getCoucheFromFile(path_site_retenu, "site_retenu")

        
        
        self.niveau = self.coucheModel.getNbrAttributsCouche(couche)
        self.list = [] # Liste dans laquelle on stocke les elements servants au filtre
        
        self.buildDocxRecursive(couche, self.coucheModel.getFilteredNiveau(couche))
        
        self.docxBuilder.writeDoc(rapport_path)

        print("rapport ecrit")

        
        
        
        
    def buildDocxRecursive(self, couche,  liste_elements):
        """Fonction recursive qui parcours pour un elt d'un niveau les elt du niveau +1"""
        
        current_nv = len(self.list)
        # Condition d'arret
        if current_nv >= self.niveau - 1:
            for elt in liste_elements:
                self.rapport = self.docxBuilder.addParagraph(elt, current_nv)
            return
        
        for elt in liste_elements:

            self.list.append(elt)
            
            self.rapport = self.docxBuilder.addParagraph(elt, current_nv)
            
            # On filtre
            nv_liste = self.coucheModel.getFilteredNiveau(couche, self.list)
            # On rappelle avec la nouvelle liste
            self.buildDocxRecursive(couche, nv_liste)
            self.list.pop()
            


    def convertToPdf(self):
        
        try:
            emplacement_rapport = self.configModel.getFromConfig("emplacement_rapport")
            nom_rapport = self.configModel.getFromConfig("nom_rapport")
            
            
            fichier_docx_entree = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport) + nom_rapport + ".docx"
            fichier_pdf_sortie = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport) + nom_rapport + '.pdf'
            dossier_pdf_sortie = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport)
        
            lo_path = os.path.dirname("C:\Program Files\LibreOffice\program\soffice.exe")

            
            # Création de la commande
            command = [
                lo_path,
                '--headless', # Ne pas lancer l'interface graphique
                '--convert-to', 'pdf',
                '--outdir', dossier_pdf_sortie,
                fichier_docx_entree
            ]
        
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=20
            )
            
            if result.returncode != 0:
                print("erreur lors de la conversion du docx en pdf pendant la commande lo")
        except Exception as e:
            print("Erreur lors de la conversion du docx en pdf")
            print(e)
            raise
        
    def handleFormTaskFinished(self, success):
        """
            Quand formTask est fini
        """
        
        self.buildRapport()
        self.dialog.accept()