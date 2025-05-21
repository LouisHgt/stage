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
        
        # Récupération du formulaire scenario
        formulaire = self.formView.getFormulaire()
        # Nbr de ligne du formulaire
        nbr_rows = formulaire.rowCount()
        
        # On parcours les lignes du formulaire
        for i in range(nbr_rows):
            
            # On récupère l'élément qui possede la comboBox
            row_formulaire = formulaire.itemAt(i).widget().layout()
            
            # On récupère la comboBox et on la met sur son dernier indice -> 'Vide'
            if isinstance(row_formulaire, QtWidgets.QHBoxLayout):
                for j in range(row_formulaire.count()):
                    if isinstance(row_formulaire.itemAt(j).widget(), QtWidgets.QComboBox):
                        comboBox = row_formulaire.itemAt(j).widget()
                        comboBox.setCurrentIndex(comboBox.count() - 1)
     
    def indiceStringToInt(self, indice_string):
        if indice_string == "Q10":
            return 10
        elif indice_string == "Q20":
            return 20
        elif indice_string == "Q50":
            return 50
        elif indice_string == "Q100":
            return 100
        elif indice_string == "Qex":
            return 1000
        elif indice_string == "AZI":
            return 10000
        elif indice_string == "Vide":
            return 0
        else:
            return 0
    
    def normalizeData(self, data):
        """
            Prend en argument les valeurs du formulaire et renvoie
            un dictionnaire avec les occurences en int
        """
        
        for key, val in data.items():
            data[key] = self.indiceStringToInt(val)
            
        return data
           
    def upperList(self, list):
        new_list = []
        
        for elt in list:
            if type(elt) == str:
                new_list.append(elt.upper())

        return new_list

    def sauvegarderBassinPressed(self, bouton):
        
        try:
            # On desactive le bouon le temps du traitement
            bouton.setEnabled(False)
            bouton.setText("Traitement...")
            bouton.repaint()
            
            # Recuperation des données necessaire à la sauvegarde de la couche
            couche_sauvegarde = self.coucheModel.getCoucheFromNom('Bassins versants')
            comboBoxValues = self.formView.getComboBoxValues()
            comboBoxValues = self.normalizeData(comboBoxValues)
            
            self.coucheModel.save_bassins(couche_sauvegarde, comboBoxValues)
            bouton.setEnabled(True)
            bouton.setText("Sauvegarder")
        except Exception as e:
            print("Probleme rencontré lors de la sauvegarde des occurences de bassins")
            print(e)
            
    def handleOccurBassinChanged(self, occur, lib_bassin):
        """
            Appelle la methode de la vue qui surligne le bassin en fonction d'un nom de bassin
            et d'une couleur
        """
        
        opacite = int(self.configModel.getFromConfig("opacite"))
        
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

        # Récupérer les valeurs nécessaires du formulaire
        combo_values = self.formView.getComboBoxValues()
        checkbox_values = self.formView.getCheckboxValues()             
        # 3. Créer l'instance de la tâche
        task_description = "Génération du rapport DDTM"
        self.current_task = FormulaireTask(
            task_description,
            self.coucheModel,
            combo_values,
            checkbox_values,
            self.dialog
        )

        # Liaison de la tâche aux handlers
        self.current_task.progressChanged.connect(self.formView.handleUpdateProgressBar)
        self.current_task.task_finished.connect(self.rapportController.handleFormTaskFinished)
        # Ajouter la tâche au gestionnaire de tâches de QGIS
        QgsApplication.taskManager().addTask(self.current_task)
        
    
