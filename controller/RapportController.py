import os

from .DocxBuilder import DocxBuilder

from qgis.PyQt import QtWidgets # type: ignore

class RapportController():
    def __init__(self, config_model_inst, couche_model_inst):
        self.configModel = config_model_inst
        self.coucheModel = couche_model_inst
        self.docxBuilder = DocxBuilder()
        
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
                self.docxBuilder.addParagraph(elt, current_nv)
            return
        
        for elt in liste_elements:

            self.list.append(elt)
            
            self.docxBuilder.addParagraph(elt, current_nv)
            
            # On filtre
            nv_liste = self.coucheModel.getFilteredNiveau(couche, self.list)
            # On rappelle avec la nouvelle liste
            self.buildDocxRecursive(couche, nv_liste)
            self.list.pop()
            


    def convertToPdf(self):
        
        try:
            emplacement_rapport = self.configModel.getFromConfig("emplacement_rapport")
            nom_rapport = self.configModel.getFromConfig("nom_rapport")
            
            
            fichier_docx_entree = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport, nom_rapport) + ".docx"
            fichier_docx_entree = "\"" + fichier_docx_entree + "\""
            
            dossier_pdf_sortie = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport)
            dossier_pdf_sortie = "\"" + dossier_pdf_sortie + "\""
        
            lo_path = "\"C:\\Program Files\\LibreOffice\\program\\soffice.exe\""
            
            bat_path = os.path.join(os.path.dirname(__file__), '..', 'etc', 'convertToPdf.bat')

            space = " "
            command = bat_path + space + fichier_docx_entree + space + dossier_pdf_sortie + space + lo_path
            # print(command)
            
            os.system(command)
            
        except Exception as e:
            print("Erreur lors de la conversion du docx en pdf")
            print(e)
            raise
        
    def handleFormTaskFinished(self, success):
        """
            Quand formTask est fini
        """
        try:
            self.buildRapport()
            
            pdfCheckBox = self.formView.dialog.findChild(QtWidgets.QCheckBox, 'pdfCheckBox')
                    
            # Conversion en pdf si précisé dans le config
            if pdfCheckBox.isChecked():
                self.convertToPdf()
            
            path = r"C:\Users\louis.huguet\Travail\Plugins\DDTM06_GenerationRapport\output"
            os.startfile(path)
            
        except Exception as e:
            print("erreur lors de l'ecriture du doc ou du pdf dans le handlerFormTaskFinished")
            print(e)
        finally:
            self.dialog.accept()