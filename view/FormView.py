from time import sleep
import os

# --- Imports QGIS ---
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes # type: ignore
from qgis.gui import QgsMapCanvas, QgsRubberBand # type: ignore

# --- Imports Qt ---
from qgis.PyQt import uic, QtWidgets, QtGui # type: ignore
from qgis.gui import QgsMapCanvas # type: ignore

from ..controller.WheelEventFilter import WheelEventFilter
from ..controller.ChangeEventFilter import ChangeEventFilter



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..\DDTM_GenerationRapport_dialog_base.ui'))


class FormView():
    
    def __init__(self, dialog, couche_model_inst, config_model_inst, rapport_controller_inst):
        self.dialog = dialog # Référence à la fenêtre UI
        # Stocker les instances
        self.coucheModel = couche_model_inst
        self.configModel = config_model_inst
        
        # Stocker les eventFilters
        self.hover_filters = []
        
        # Stocker les rubberBands
        self.rubber_bands = {}
        
        # Stocker le canvas créé
        self.canvas = None

    def createRubberBand(self):
        return
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
        
    def getFormulaire(self):
        return self.dialog.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
        
        
    def highlightBassin(self, lib_bassin, couleur = None):
        """
            Highlight une zone si le libelé est précisé,
            sinon ne higlight rien
        """  
        # Récupération du rubber band ou creation
        if lib_bassin in self.rubber_bands:
            current_rubber = self.rubber_bands.get(lib_bassin)
        else :
            # Création d'un nouveau rubberBand
            current_rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
           
            # Récupération de la geom
            geom = self.bassins_geom.get(lib_bassin)        
            current_rubber.setToGeometry(geom, None)
            
            # Ajout au dictionnaire
            self.rubber_bands[lib_bassin] = current_rubber
        
        # Gestion de la couleur
        current_rubber.hide()
        # cacher le rubber band si occur == "Vide"
        if couleur != None:
            current_rubber.hide()
            current_rubber.setColor(couleur)
            current_rubber.show()
        else:
            return
            
            
            
    
    def setupCanvas(self):
        """Setup du canvas"""
        
        try:
            # Gestion des couches
            couche_fond = self.coucheModel.getCoucheFromNom('N_ORTHO_2023_COUL_006')
            couche_bassin = self.coucheModel.getCoucheFromNom('Bassins versants')
            couche_cours_eau = self.coucheModel.getCoucheFromNom('Cours_d_eau_principaux')
            if not couche_fond.isValid() and not couche_bassin.isValid():
                print('pas valide')
            
            # Creation du canvas
            self.canvas = QgsMapCanvas()
            self.canvas.setProject(QgsProject().instance())
            self.canvas.setExtent(couche_bassin.extent())
            self.canvas.setLayers([couche_cours_eau, couche_bassin, couche_fond])
                    
            # Gestion du zoom
            self.wheel_filter = WheelEventFilter(self.canvas)
            self.canvas.viewport().installEventFilter(self.wheel_filter)
            
            # Creation du rubber band
            self.hover_rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            self.hover_rubber.setWidth(2)
            
            # Ajout au formulaire
            conainer = self.dialog.findChild(QtWidgets.QVBoxLayout, 'container_canvas')
            conainer.insertWidget(0, self.canvas)
        except Exception as e:
            print("Erreur lors de la création du canvas")
            print(e)
            raise


    def setupFormulaireScenario(self, formController):
        """Setup du formulaire de scenario."""

        try:
            
            # Recuperation du conteneur principal QT
            container_scenario = self.dialog.findChild(QtWidgets.QWidget, 'container_scenario')
            
            # --------------------- Choix de l'indice de retour par bassin. -------------------
            
            # Recuperation des indices depuis le fichier de config
            indices = self.configModel.getFromConfig('indices')

            
            # Recuperation des bassins depuis la couche QGis
            nom_couche_bassins = self.configModel.getFromConfig('nom_couche_bassins')
            libelle_bassins = self.configModel.getFromConfig('libelle_couche_bassins')
            
            # Recupération de la couche Bassins_versants
            bassins_versants = self.coucheModel.getCoucheFromNom(nom_couche_bassins)
            
            bassins = []
            bassins_retires = formController.upperList(self.configModel.getFromConfig("bassins_retires"))
            self.bassins_geom = {}
            # On parcourt la liste des couches pour récupérer leur noms
            for feature in bassins_versants.getFeatures():
                
                # Récupération du nom
                bassin = feature[libelle_bassins]
                if bassin not in bassins_retires:
                    bassins.append(bassin)
                
                    # Récupération de la geometrie
                    geom = feature.geometry()
                    self.bassins_geom[bassin] = geom
                
                
            
            # Ajout d'un formulaire de scenario
            formulaire = container_scenario.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
            
            # Dictiopnnaire pour stocket les comboboxes
            self.dialog.combo_boxes = {}
            
            hauteur_minimum_ligne_formulaire = 25
            for bassin in bassins:
                
                # 1. Créer un QWidget conteneur pour la ligne entière
                row_widget = QtWidgets.QWidget()

                # 2. Créer un layout pour ce QWidget conteneur (par exemple QHBoxLayout)
                row_layout = QtWidgets.QHBoxLayout(row_widget) # Applique directement le layout au widget
                row_layout.setContentsMargins(0, 0, 0, 0) # Optionnel: pour que le hover soit précis
                row_layout.setSpacing(2)                  # Optionnel: espacement entre label et combobox
                
    
                # Ajout d'un label pour chaque bassin
                label = QtWidgets.QLabel(bassin)
                label.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                # Ajout d'un combobox pour chaque bassin
                comboBox = QtWidgets.QComboBox()
                comboBox.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                comboBox.addItems(indices)
                comboBox.setCurrentIndex(comboBox.count() - 1)
                
                # Ajouter la comboBox et le layout à la ligne
                row_layout.addWidget(label)
                row_layout.addWidget(comboBox)
                
                
                # Création du filtre pour hover
                #event_filter = ChangeEventFilter(bassin, self)
                #row_widget.installEventFilter(event_filter)
                
                # Lisaison de la combobox au handler pour surligner le bassin
                comboBox.currentTextChanged.connect(
                    lambda new_text, lib_bassin=label.text(): 
                        formController.handleOccurBassinChanged(
                            new_text,
                            lib_bassin
                        )
                )

                # Stocker la combobox dans le dictionnaire
                self.dialog.combo_boxes[bassin] = comboBox
                # Stocker l'event filter pour nepas perdre la reference
                #self.hover_filters.append(event_filter)
                
                # Installation du filtre sur
                formulaire.addRow(row_widget)

            

        except Exception as e:
            print(f"Une erreur s'est produite dans setupFormulaireScenario : {e}")
            self.dialog.close()
            raise


    def mapTypes(self, couche_type):
        colonne_id = "id"
        colonne_nom = "nom"
        colonne_code = "code"
        
        codes = {}
        types = {}
        for feature in couche_type.getFeatures():
            types[feature[colonne_id]] = feature[colonne_nom]
            codes[feature[colonne_id]] = feature[colonne_code]

        return (types, codes)
        
    def setupFormulaireSensibilite(self):
        try:
            # Recuperation des elements de la fenetre QT
            project = QgsProject.instance()
            container_sensibilite = self.dialog.findChild(QtWidgets.QWidget, 'container_formulaires').findChild(QtWidgets.QWidget, 'container_sensibilite')
            formulaire = container_sensibilite.findChild(QtWidgets.QFormLayout, 'formulaire_sensibilite')
            
            
            
            # Recuperation des types utilisés depuis la couche QGis
            nom_couche_type = self.configModel.getFromConfig('nom_couche_type')
            if nom_couche_type == "":  # Si getFromConfig ne renvoie rien
                nom_couche_type = "type_etendu"  # Valeur par défaut
            else:
                nom_couche_type = nom_couche_type  # Récupérer la première valeur
            
            couche_types = project.mapLayersByName(nom_couche_type)[0]
            
            (types, codes) = self.mapTypes(couche_types)
            # Dictionnaire pour stocker l'etat des checkboxes en fonction du type
            self.dialog.checkboxes = {}
            
            # Types de sites à exclure
            types_retires = self.configModel.getFromConfig("types_retires")
            
            # On parcours les types de la couche "type" pour créer le formulaire
            for id, nom in types.items():
                # On vérifie que les type ne fait pas partie des exclus
                if codes.get(id) not in types_retires:
                    # Ajout d'un label pour chaque type de site
                    label = QtWidgets.QLabel(nom)
                    label.setMinimumHeight(25)
                    # Ajout d'un checkbox pour chaque type de site
                    checkBox = QtWidgets.QCheckBox()
                    checkBox.setMinimumHeight(25)
                    
                    if self.configModel.getFromConfig("sites_coches") == "1":
                        checkBox.setChecked(True)
                    else:
                        checkBox.setChecked(False)
                    
                    # Stockage de la checkbox dans le dictionnaire
                    self.dialog.checkboxes[id] = checkBox
                    
                    # Ajout du label et du combobox au formulaire
                    formulaire.addRow(checkBox, label)
            
            
        except Exception as e:
            print(f"Une erreur s'est produite dans setupFormulaireSensibilite : {e}")
            self.dialog.close()
            raise
        
    def setupProgressBar(self):
        
        pdfCheckBox = self.dialog.findChild(QtWidgets.QCheckBox, 'pdfCheckBox')
        pdfCheckBox.hide()
        
        containerFooter = self.dialog.findChild(QtWidgets.QVBoxLayout, 'container_footer')
                
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
        
        containerFooter.addWidget(self.progressBar)
    
    def handleUpdateProgressBar(self, percentage_value):
        
        self.progressBar.setValue(int(percentage_value))
        
    def setupButtons(self, formController):
        """Setup des boutons de la fenetre QT."""
        boutonValider = self.dialog.findChild(QtWidgets.QPushButton, 'valider')
        boutonValider.clicked.connect(lambda: formController.pressed(boutonValider))
        
        bouton_reinitialiser = self.dialog.findChild(QtWidgets.QPushButton, 'bouton_reinitialiser')
        bouton_reinitialiser.clicked.connect(lambda: formController.reinitialiserPressed())
        
        bouton_save_bassins = self.dialog.findChild(QtWidgets.QPushButton, 'bouton_save_bassins')
        bouton_save_bassins.clicked.connect(lambda: formController.sauvegarderBassinPressed(bouton_save_bassins))
        
        pdfCheckBox = self.dialog.findChild(QtWidgets.QCheckBox, 'pdfCheckBox')
        
        if self.configModel.getFromConfig('convertir_en_pdf') == '1':
            pdfCheckBox.setChecked(True)
        else:
            pdfCheckBox.setChecked(False)