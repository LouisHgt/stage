from ..view.FormView import FormView
from .FormulaireTask import FormulaireTask

# --- Imports QGIS Core ---
from qgis.core import QgsApplication # type: ignore

# --- Imports Qt ---
from qgis.PyQt import QtWidgets, QtGui # type: ignore


class FormController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.dialog = dialog
        # Stocker les instances reçues
        self.coucheModel = couche_model_inst
        self.configModel = config_model_inst
        self.rapportController = rapport_controller_inst
        
        # Instancier la vue en passant les instances
        self.formView = FormView(dialog, self.coucheModel, self.configModel, self.rapportController)
        self.rapportController.setFormView(self.formView) # Passage de formView à rapportController
        self.rapportController.setDialog(self.dialog)
        self.current_task = None
    
    def setupFormulaires(self):
        """Configure les formulaires."""
        self.formView.setupFormulaireScenario(self)
        self.formView.setupFormulaireSensibilite()
        self.formView.setupCanvas()
        self.formView.setupButtons(self)
        
    def reinitialiserPressed(self):
        '''
            Remets toutes les comboBox du formulaire scenario
            à 'Vide'
        '''
        formulaire = self.formView.getFormulaire('formulaire_scenario')
        nbr_rows = formulaire.rowCount()
        
        for i in range(nbr_rows):
            row_formulaire = formulaire.itemAt(i).widget().layout()
            
            if isinstance(row_formulaire, QtWidgets.QHBoxLayout):
                for j in range(row_formulaire.count()):
                    if isinstance(row_formulaire.itemAt(j).widget(), QtWidgets.QComboBox):
                        comboBox = row_formulaire.itemAt(j).widget()
                        comboBox.setCurrentIndex(comboBox.count() - 1)
     
    def setSensibilite(self, state):
        """
        Methode qui set toutes les cases à true ou false en fonction du status passé en argument
        """
        formulaire = self.formView.getFormulaire('formulaire_sensibilite')
        nbr_rows = formulaire.rowCount()

        for i in range(formulaire.count()):
            # Le layout est un QFormLayout, les widgets sont accessibles via itemAt(i).widget()
            widget = formulaire.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(state)
            
    def stringToInt(self, listOfString):
        listOfInt = []
        for string in listOfString:
            if string.strip().isdigit():
                listOfInt.append(int(string.strip()))
        return listOfInt
    
    def setFiltreSensibilite(self):
        # --- DEBUT MODIFICATION ---
        # Les types à cocher, récupérés comme une liste
        types_coches = self.configModel.getFromConfig('types_coches', as_list=True)
        # --- FIN MODIFICATION ---
        types_coches = self.stringToInt(types_coches)
        
        formulaire = self.formView.getFormulaire('formulaire_sensibilite')
            
        # Parcourir les QCheckBox stockées dans la vue
        for id_type, checkbox in self.formView.dialog.checkboxes.items():
            if id_type in types_coches:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
     
    def indiceStringToInt(self, indice_string):
        if indice_string == "Q10": return 10
        elif indice_string == "Q20": return 20
        elif indice_string == "Q50": return 50
        elif indice_string == "Q100": return 100
        elif indice_string == "Qex": return 1000
        elif indice_string == "AZI": return 10000
        else: return 0
    
    def normalizeData(self, data):
        """
            Prend en argument les valeurs du formulaire et renvoie
            un dictionnaire avec les occurences en int
        """
        normalized = {}
        for key, val in data.items():
            normalized[key] = self.indiceStringToInt(val)
        return normalized
               
    def upperList(self, lst):
        """
        Renvoie une liste de string en majuscule, en gérant les chaînes vides
        """
        return [elt.upper() for elt in lst if isinstance(elt, str) and elt.strip()]

    def sauvegarderBassinPressed(self, bouton):
        """
        Methode appellée quand on appuie sur le bouton pour sauvegarder les 
        indices correspondants aux bassins dans la couche Bassins versants
        """
        try:
            bouton.setEnabled(False)
            bouton.setText("Traitement...")
            bouton.repaint()
            
            nom_couche_bassins = self.configModel.getFromConfig('nom_couche_bassins')
            couche_sauvegarde = self.coucheModel.getCoucheFromNom(nom_couche_bassins)
            comboBoxValues = self.formView.getComboBoxValues()
            comboBoxValues = self.normalizeData(comboBoxValues)
            
            self.coucheModel.save_bassins(couche_sauvegarde, comboBoxValues)
            bouton.setEnabled(True)
            bouton.setText("Sauvegarder")
        except Exception as e:
            print(f"Probleme rencontré lors de la sauvegarde des occurences de bassins: {e}")
            raise
            
    def handleOccurBassinChanged(self, occur, lib_bassin):
        """
            Appelle la methode de la vue qui surligne le bassin en fonction d'un nom de bassin
            et d'une couleur
        """
        opacite = int(self.configModel.getFromConfig("opacite") or 100)
        
        couleurs_dic = {
            "Q10": QtGui.QColor(12, 238, 254, opacite),
            "Q20": QtGui.QColor(113, 222, 255, opacite),
            "Q30": QtGui.QColor(0, 129, 250, opacite),
            "Q50": QtGui.QColor(152, 0, 240, opacite),
            "Q100": QtGui.QColor(246, 149, 230, opacite),
            "Qex": QtGui.QColor(246, 107, 0, opacite),
            "AZI": QtGui.QColor(254, 4, 8, opacite),
            "Vide": None
        }
        
        couleur = couleurs_dic.get(occur)
        
        if couleur is None:
            self.formView.highlightBassin(lib_bassin)
        else:
            self.formView.highlightBassin(lib_bassin, couleur)
            
    def pressed(self, boutonValider):
        """
            Affiche les données et les inscrit dans des couches
            Crée le rapport docx
            Ferme la boite de dialogue
        """
        boutonValider.setEnabled(False)
        boutonValider.setText('Traitement...')
        self.formView.setupProgressBar()

        combo_values = self.formView.getComboBoxValues()
        checkbox_values = self.formView.getCheckboxValues()             
        
        task_description = "Génération du rapport DDTM"
        self.current_task = FormulaireTask(
            task_description,
            self.coucheModel,
            combo_values,
            checkbox_values,
            self.dialog
        )

        self.current_task.progressChanged.connect(self.formView.handleUpdateProgressBar)
        self.current_task.task_finished.connect(self.rapportController.handleFormTaskFinished)
        QgsApplication.taskManager().addTask(self.current_task)