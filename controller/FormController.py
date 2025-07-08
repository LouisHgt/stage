from ..view.FormView import FormView
from .FormulaireTask import FormulaireTask
from qgis.core import QgsApplication # type: ignore
from qgis.PyQt import QtWidgets, QtGui # type: ignore

class FormController():
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.dialog = dialog
        self.coucheModel = couche_model_inst
        self.configModel = config_model_inst
        self.rapportController = rapport_controller_inst
        
        self.formView = FormView(dialog, self.coucheModel, self.configModel, self.rapportController)
        self.rapportController.setFormView(self.formView)
        self.rapportController.setDialog(self.dialog)
        self.current_task = None
    
    def setupFormulaires(self):
        self.formView.setupFormulaireScenario(self)
        self.formView.setupFormulaireSensibilite()
        self.formView.setupCanvas()
        self.formView.setupButtons(self)
        
    def reinitialiserPressed(self):
        formulaire = self.formView.getFormulaire('formulaire_scenario')
        for i in range(formulaire.rowCount()):
            row_formulaire = formulaire.itemAt(i).widget().layout()
            if isinstance(row_formulaire, QtWidgets.QHBoxLayout):
                for j in range(row_formulaire.count()):
                    if isinstance(row_formulaire.itemAt(j).widget(), QtWidgets.QComboBox):
                        comboBox = row_formulaire.itemAt(j).widget()
                        comboBox.setCurrentIndex(comboBox.count() - 1)
     
    def setSensibilite(self, state):
        formulaire = self.formView.getFormulaire('formulaire_sensibilite')
        for i in range(formulaire.count()):
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
        types_coches = self.configModel.getFromConfig('types_coches', as_list=True)
        types_coches = self.stringToInt(types_coches)
        
        for id_type, checkbox in self.formView.dialog.checkboxes.items():
            checkbox.setChecked(id_type in types_coches)
     
    def indiceStringToInt(self, indice_string):
        mapping = {"Q10": 10, "Q20": 20, "Q50": 50, "Q100": 100, "Qex": 1000, "AZI": 10000}
        return mapping.get(indice_string, 0)
    
    def normalizeData(self, data):
        return {key: self.indiceStringToInt(val) for key, val in data.items()}
               
    def upperList(self, lst):
        return [elt.upper() for elt in lst if isinstance(elt, str) and elt.strip()]

    def sauvegarderBassinPressed(self, bouton):
        try:
            bouton.setEnabled(False)
            bouton.setText("Traitement...")
            bouton.repaint()
            
            nom_couche_bassins = self.configModel.getFromConfig('nom_couche_bassins')
            couche_sauvegarde = self.coucheModel.getCoucheFromNom(nom_couche_bassins)
            if couche_sauvegarde:
                comboBoxValues = self.formView.getComboBoxValues()
                comboBoxValues = self.normalizeData(comboBoxValues)
                self.coucheModel.save_bassins(couche_sauvegarde, comboBoxValues)
            else:
                print(f"Couche de sauvegarde '{nom_couche_bassins}' non trouvée.")

            bouton.setEnabled(True)
            bouton.setText("Sauvegarder")
        except Exception as e:
            print(f"Probleme rencontré lors de la sauvegarde des occurences de bassins: {e}")
            raise
            
    def handleOccurBassinChanged(self, occur, lib_bassin):
        opacite_str = self.configModel.getFromConfig("opacite")
        opacite = int(opacite_str) if opacite_str.isdigit() else 100
        
        couleurs_dic = {
            "Q10": QtGui.QColor(12, 238, 254, opacite),
            "Q20": QtGui.QColor(113, 222, 255, opacite),
            "Q50": QtGui.QColor(152, 0, 240, opacite),
            "Q100": QtGui.QColor(246, 149, 230, opacite),
            "Qex": QtGui.QColor(246, 107, 0, opacite),
            "AZI": QtGui.QColor(254, 4, 8, opacite)
        }
        
        couleur = couleurs_dic.get(occur)
        self.formView.highlightBassin(lib_bassin, couleur)
            
    def pressed(self, boutonValider):
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