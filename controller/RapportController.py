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
        emplacement_rapport = self.configModel.getFromConfig("emplacement_rapport")
        nom_rapport = self.configModel.getFromConfig("nom_rapport")
        rapport_path = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport, nom_rapport) + ".docx"

        self.docxBuilder.initDoc()
    
        emplacement_couche_site_retenu = self.configModel.getFromConfig('emplacement_couche_site_retenu')
        nom_couche_site_retenu = self.configModel.getFromConfig('nom_couche_site_retenu')
        path_site_retenu = os.path.join(os.path.dirname(__file__), '..', emplacement_couche_site_retenu, nom_couche_site_retenu) + ".shp"
        
        try:
            couche = self.coucheModel.getCoucheFromFile(path_site_retenu, "site_retenu")
            if not couche:
                print(f"La couche des sites retenus n'a pas pu être chargée depuis {path_site_retenu}")
                return
        except Exception as e:
            print(f"Erreur lors du chargement de la couche des sites retenus: {e}")
            return
            
        self.niveau = self.coucheModel.getNbrAttributsCouche(couche)
        self.list = []
        
        self.buildDocxRecursive(couche, self.coucheModel.getFilteredNiveau(couche))
        self.docxBuilder.writeDoc(rapport_path)
            
        print("Rapport écrit")
        
    def buildDocxRecursive(self, couche, liste_elements):
        current_nv = len(self.list)
        if current_nv >= self.niveau - 1:
            for elt in liste_elements:
                self.docxBuilder.addParagraph(elt, current_nv)
            return
        
        for elt in liste_elements:
            self.list.append(elt)
            self.docxBuilder.addParagraph(elt, current_nv)
            nv_liste = self.coucheModel.getFilteredNiveau(couche, self.list)
            self.buildDocxRecursive(couche, nv_liste)
            self.list.pop()
            
    def convertToPdf(self):
        try:
            emplacement_rapport = self.configModel.getFromConfig("emplacement_rapport")
            nom_rapport = self.configModel.getFromConfig("nom_rapport")
            
            fichier_docx_entree = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport, nom_rapport) + ".docx"
            fichier_docx_entree = f'"{fichier_docx_entree}"'
            
            dossier_pdf_sortie = os.path.join(os.path.dirname(__file__), '..', emplacement_rapport)
            dossier_pdf_sortie = f'"{dossier_pdf_sortie}"'
        
            lo_path = '"C:\\Program Files\\LibreOffice\\program\\soffice.exe"'
            bat_path = os.path.join(os.path.dirname(__file__), '..', 'etc', 'convertToPdf.bat')

            command = f'{bat_path} {fichier_docx_entree} {dossier_pdf_sortie} {lo_path}'
            os.system(command)
        except Exception as e:
            print(f"Erreur lors de la conversion du docx en pdf: {e}")
            raise
        
    def handleFormTaskFinished(self, success):
        if not success:
            print("La tâche FormTask a échoué. La génération du rapport est annulée.")
            self.dialog.reject()
            return

        try:
            self.buildRapport()
            
            pdfCheckBox = self.formView.dialog.findChild(QtWidgets.QCheckBox, 'pdfCheckBox')
            if pdfCheckBox and pdfCheckBox.isChecked():
                self.convertToPdf()
            
            path = os.path.join(os.path.dirname(__file__), '..', 'output')
            if os.path.exists(path):
                os.startfile(path)
            
        except Exception as e:
            print(f"Erreur lors de l'ecriture du doc ou du pdf dans le handlerFormTaskFinished: {e}")
        finally:
            self.dialog.accept()