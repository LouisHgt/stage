from time import sleep
import os
from .coucheManager import coucheManager
from .configManager import configManager
from .rapportBuilder import rapportBuilder


# --- Imports QGIS ---
from qgis.core import QgsProject, QgsVectorLayer, QgsMessageLog, Qgis # type: ignore

# --- Imports Qt ---
from qgis.PyQt import uic # type: ignore
from qgis.PyQt import QtWidgets # type: ignore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'DDTM_GenerationRapport_dialog_base.ui'))

class formBuilder(QtWidgets.QDialog, FORM_CLASS):
    
    
    def __init__(self, dialog):
        """Constructor."""
        project = QgsProject.instance()
        self.dialog = dialog
        self.coucheManager = coucheManager(project)
        self.configManager = configManager()
        self.rapportBuilder = rapportBuilder(self.coucheManager)
        
        

    def getComboBoxValues(self):
        """Récupère les valeurs sélectionnées dans les QComboBox."""
        values = {}
        for bassin, comboBox in self.dialog.combo_boxes.items():
            values[bassin] = comboBox.currentText()
        return values

    def getCheckboxValues(self): 
        values = {}
        for type, checkBox in self.dialog.checkboxes.items():
            values[type] = checkBox.isChecked()
        return values

    def pressed(self):
        """
            Affiche les données et les inscrit dans des couches
            Crée le rapport docx
            Ferme la boite de dialogue
        """
        
        # print(self.getComboBoxValues())
        # print(self.getCheckboxValues())
        
        self.coucheManager.clearTmpFolder()
        self.coucheManager.createStatusSensibilite(self.getCheckboxValues())
        self.coucheManager.createStatusScenario(self.getComboBoxValues())
        self.coucheManager.createSiteRetenu()
        
        self.rapportBuilder.buildRapport(".docx")
        output = os.path.join(os.path.dirname(__file__), 'tmp')
        
        # Suppression des objets non referencés
        import gc
        gc.collect()
        
        
        self.dialog.accept()
        

    def setupFormulaireScenario(self):
        """Setup du formulaire de scenario."""

        try:
            
            # Recuperation du conteneur principal QT
            container_scenario = self.dialog.findChild(QtWidgets.QWidget, 'container_formulaires').findChild(QtWidgets.QWidget, 'container_scenario')
            
            # --------------------- Choix de l'indice de retour par bassin. -------------------
            
            # Recuperation des indices depuis le fichier de config
            indices = self.configManager.getFromConfig('indices')

            
            # Recuperation des bassins depuis la couche QGis
            nom_couche_bassins = self.configManager.getFromConfig('nom_couche_bassins')[0]
            libelle_bassins = self.configManager.getFromConfig('libelle_couche_bassins')[0]
            
            # Recupération de la couche Bassins_versants
            bassins_versants = self.coucheManager.getCoucheFromNom(nom_couche_bassins)
            
            bassins = []
            # On parcourt la liste des couches pour récupérer leur noms
            for feature in bassins_versants.getFeatures():
                bassin = feature[libelle_bassins]
                bassins.append(bassin)
            
            # Ajout d'un formulaire de scenario
            formulaire = container_scenario.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
            
            # Dictiopnnaire pour stocket les comboboxes
            self.dialog.combo_boxes = {}
            
            hauteur_minimum_ligne_formulaire = 25
            for bassin in bassins:
                # Ajout d'un label pour chaque bassin
                label = QtWidgets.QLabel(bassin)
                label.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                # Ajout d'un combobox pour chaque bassin
                comboBox = QtWidgets.QComboBox()
                comboBox.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                comboBox.addItems(indices)
                
                # Stocker la combobox dans le dictionnaire
                self.dialog.combo_boxes[bassin] = comboBox
                
                formulaire.addRow(label, comboBox)

            

        except Exception as e:
            print(f"Une erreur s'est produite dans setupFormulaireScenario : {e}")
            self.dialog.close()
            raise


    def mapTypes(self, couche_type):
        colonne_id = "id"
        colonne_nom = "nom"
        
        
        types = {}
        for feature in couche_type.getFeatures():
            types[feature[colonne_id]] = feature[colonne_nom]

        return types
        
    def setupFormulaireSensibilite(self):
        try:
            # Recuperation des elements de la fenetre QT
            project = QgsProject.instance()
            container_sensibilite = self.dialog.findChild(QtWidgets.QWidget, 'container_formulaires').findChild(QtWidgets.QWidget, 'container_sensibilite')
            formulaire = container_sensibilite.findChild(QtWidgets.QFormLayout, 'formulaire_sensibilite')
            
            # Recuperation des types utilisés depuis la couche QGis
            nom_couche_type = self.configManager.getFromConfig('nom_couche_type')
            if nom_couche_type[0] == "":  # Si getFromConfig ne renvoie rien
                nom_couche_type = "type_etendu"  # Valeur par défaut
            else:
                nom_couche_type = nom_couche_type[0]  # Récupérer la première valeur
            
            couche_types = project.mapLayersByName(nom_couche_type)[0]
            
            types = self.mapTypes(couche_types)
            
            # Dictionnaire pour stocker l'etat des checkboxes en fonction du type
            self.dialog.checkboxes = {}
            
            # On parcours les types de la couche "type" pour créer le formulaire
            for id, nom in types.items():
                # Ajout d'un label pour chaque type de site
                label = QtWidgets.QLabel(nom)
                label.setMinimumHeight(25)
                # Ajout d'un checkbox pour chaque type de site
                checkBox = QtWidgets.QCheckBox()
                checkBox.setMinimumHeight(25)
                checkBox.setChecked(True)
                
                # Stockage de la checkbox dans le dictionnaire
                self.dialog.checkboxes[id] = checkBox
                
                # Ajout du label et du combobox au formulaire
                formulaire.addRow(checkBox, label)
            
            
        except Exception as e:
            print(f"Une erreur s'est produite dans setupFormulaireSensibilite : {e}")
            self.dialog.close()
            raise
        
        
    def setupButtons(self):
        """Setup des boutons de la fenetre QT."""
        boutonValider = self.dialog.findChild(QtWidgets.QPushButton, 'valider')
        boutonValider.clicked.connect(lambda: self.pressed())