from time import sleep
import configparser
import os


# --- Imports QGIS ---
from qgis.core import QgsProject, QgsVectorLayer, QgsMessageLog, Qgis

# --- Imports Qt ---
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'DDTM_GenerationRapport_dialog_base.ui'))

def getFromConfig(key):        
    """Recupere les indices de retour depuis le fichier de config.

    Retourne :
        liste des indices de retour
    """

    #Emplacement du fichier de config
    config_path = os.path.join(os.path.dirname(__file__), 'etc', 'Config.cfg')

    #Instance d'un parseur de config
    config = configparser.ConfigParser()

    #Liste des indices retour
    liste = []
    if os.path.exists(config_path):
        config.read(config_path)
        if 'Datas' in config and key in config['Datas']:
            liste = config['Datas'][key].split(',')
        else:
            print("Aucun indice de retour trouvé dans le fichier de config.")
    else:
        print("Le fichier de config n'existe pas.")

    print(liste)
    return liste

def getComboBoxValues(self):
    """Récupère les valeurs sélectionnées dans les QComboBox."""
    values = {}
    for bassin, comboBox in self.combo_boxes.items():
        values[bassin] = comboBox.currentText()
    return values

def pressed(self):
    print("Bouton valider presse")
    getComboBoxValues(self)
    self.close()

def setupFormulaireScenario(self):
    """Setup du formulaire de scenario."""

    try:
        # Recuperation du projet actif QGis
        project = QgsProject.instance()
        print(project)
        
        
        # Recuperation du conteneur principal QT
        container_scenario = self.findChild(QtWidgets.QWidget, 'container_formulaires').findChild(QtWidgets.QWidget, 'container_scenario')
        
        # --------------------- Choix de l'indice de retour par bassin. -------------------
        
        # Recuperation des indices depuis le fichier de config
        indices = getFromConfig('indices')

        
        # Recuperation des bassins depuis la couche QGis
        nom_couche_bassins = getFromConfig('nom_couche_bassins')[0]
        libelle_bassins = getFromConfig('libelle_couche_bassins')[0]
        
        # Recupération de la couche Bassins_versants
        bassins_versants = project.mapLayersByName(nom_couche_bassins)[0]
        
        bassins = []
        # On parcourt la liste des couches pour récupérer leur noms
        for feature in bassins_versants.getFeatures():
            bassin = feature[libelle_bassins]
            bassins.append(bassin)
        
        # Ajout d'un formulaire de scenario
        formulaire = container_scenario.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
        
        # Dictiopnnaire pour stocket les comboboxes
        self.combo_boxes = {}
        
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
            self.combo_boxes[bassin] = comboBox
            
            formulaire.addRow(label, comboBox)

        boutonValider = self.findChild(QtWidgets.QPushButton, 'valider')
        boutonValider.clicked.connect(lambda: pressed(self))

    except Exception as e:
        print(f"Une erreur s'est produite dans setupFormulaireScenario : {e}")
        self.close()
        raise


def setupFormulaireSensibilite(self):
    try:
        print("Setup du formulaire de sensibilite")
    except Exception as e:
        print(f"Une erreur s'est produite dans setupFormulaireSensibilite : {e}")
        self.close()
        raise