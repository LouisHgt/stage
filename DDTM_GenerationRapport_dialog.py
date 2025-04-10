# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DDTM_GenerationRapportDialog
                                 A QGIS plugin
 DDTM_GenerationRapport
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-04-09
        git sha              : $Format:%H$
        copyright            : (C) 2025 by louislestagiaire
        email                : lshgt@hotmail.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import configparser
from time import sleep

# --- Imports QGIS ---
from qgis.core import QgsProject, QgsVectorLayer, QgsMessageLog, Qgis

# --- Imports Qt ---
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'DDTM_GenerationRapport_dialog_base.ui'))


class DDTM_GenerationRapportDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def getFromConfig(self, key):        
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
        
        return liste
    
    
    def pressed(self):
        print("Bouton valider presse")
        self.close()

    def setupFormulaireScenario(self):
        """Setup du formulaire de scenario."""
        # Recuperation du projet actif QGis
        if not QgsProject.instance().mapLayers():
            print("Aucun projet actif QGis.")
            sleep(1)
            self.close()
            return
            
        
        try:

            project = QgsProject.instance()
            
            
            # Recuperation du conteneur principal QT
            main_container = self.findChild(QtWidgets.QWidget, 'main_container')
            
            # --------------------- Choix de l'indice de retour par bassin. -------------------
            
            # Recuperation des indices depuis le fichier de config
            indices = self.getFromConfig('indices')
            if not indices:
                print("Aucun indice de retour trouvé dans le fichier de config.")
                sleep(1)
                self.close()
                return
            
            # Recuperation des bassins depuis la couche QGis
            nom_couche_bassins = self.getFromConfig('nom_couche_bassins')[0]
            libelle_bassins = self.getFromConfig('libelle_couche_bassins')[0]
            
            # Recupération de la couche Bassins_versants
            bassins_versants = project.mapLayersByName(nom_couche_bassins)[0]
            
            bassins = []
            # On parcourt la liste des couches pour récupérer leur noms
            for feature in bassins_versants.getFeatures():
                bassin = feature[libelle_bassins]
                bassins.append(bassin)
            
            # Ajout d'un formulaire de scenario
            formulaire = main_container.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
            
            hauteur_minimum_ligne_formulaire = 25
            print(len(bassins))
            for bassin in bassins:
                # Ajout d'un label pour chaque bassin
                label = QtWidgets.QLabel(bassin)
                label.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                # Ajout d'un combobox pour chaque bassin
                comboBox = QtWidgets.QComboBox()
                comboBox.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                comboBox.addItems(indices)
                
                formulaire.addRow(label, comboBox)

            boutonValider = main_container.findChild(QtWidgets.QPushButton, 'valider')
            boutonValider.clicked.connect(self.pressed)
        
        except Exception as e:
            print(f"Une erreur s'est produite dans setupFormulaireScenario : {e}")
            self.close()
        
    def __init__(self, parent=None):
        """Constructor."""
        super(DDTM_GenerationRapportDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setupFormulaireScenario()



