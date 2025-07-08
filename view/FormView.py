from time import sleep
import os

# --- Imports QGIS ---
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes # type: ignore
from qgis.gui import QgsMapCanvas, QgsRubberBand # type: ignore

# --- Imports Qt ---
from qgis.PyQt import uic, QtWidgets, QtGui # type: ignore
from qgis.gui import QgsMapCanvas # type: ignore

from ..controller.WheelEventFilter import WheelEventFilter
from ..model.ConfigModel import ConfigModel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..\\DDTM_GenerationRapport_dialog_base.ui'))

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
        
    def getFormulaire(self, nom_formulaire):
        return self.dialog.findChild(QtWidgets.QFormLayout, nom_formulaire)
        
    def highlightBassin(self, lib_bassin, couleur = None):
        """
            Highlight une zone si le libelé est précisé,
            sinon ne higlight rien
        """  
        if lib_bassin in self.rubber_bands:
            current_rubber = self.rubber_bands.get(lib_bassin)
        else :
            current_rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            geom = self.bassins_geom.get(lib_bassin)        
            current_rubber.setToGeometry(geom, None)
            self.rubber_bands[lib_bassin] = current_rubber
        
        current_rubber.hide()
        if couleur != None:
            current_rubber.setColor(couleur)
            current_rubber.show()

    def setupCanvas(self):
        """Setup du canvas"""
        try:
            couche_fond = self.coucheModel.getCoucheFromNom(self.configModel.getFromConfig('nom_couche_fond'))
            couche_bassin = self.coucheModel.getCoucheFromNom(self.configModel.getFromConfig('nom_couche_bassins'))
            couche_cours_eau = self.coucheModel.getCoucheFromNom(self.configModel.getFromConfig('nom_couche_cours_d_eau'))
            
            if not all([couche_fond, couche_bassin, couche_cours_eau]) or not all([l.isValid() for l in [couche_fond, couche_bassin, couche_cours_eau]]):
                print('Une ou plusieurs couches de contexte sont invalides ou non trouvées.')
                # Optionnel: on peut décider de ne pas afficher le canvas si les couches manquent.
                return

            self.canvas = QgsMapCanvas()
            self.canvas.setProject(QgsProject.instance())
            self.canvas.setExtent(couche_bassin.extent())
            self.canvas.setLayers([couche_cours_eau, couche_bassin, couche_fond])
                    
            self.wheel_filter = WheelEventFilter(self.canvas)
            self.canvas.viewport().installEventFilter(self.wheel_filter)
            
            self.hover_rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            self.hover_rubber.setWidth(2)
            
            container = self.dialog.findChild(QtWidgets.QVBoxLayout, 'container_canvas')
            container.insertWidget(0, self.canvas)
        except Exception as e:
            print(f"Erreur lors de la création du canvas : {e}")

    def setupFormulaireScenario(self, formController):
        """Setup du formulaire de scenario."""
        try:
            container_scenario = self.dialog.findChild(QtWidgets.QWidget, 'container_scenario')
            
            # --- DEBUT MODIFICATION ---
            # Recuperation des indices en spécifiant qu'on veut une liste
            indices = self.configModel.getFromConfig('indices', as_list=True)
            # --- FIN MODIFICATION ---
            
            nom_couche_bassins = self.configModel.getFromConfig('nom_couche_bassins')
            libelle_bassins = self.configModel.getFromConfig('libelle_couche_bassins')
            
            bassins_versants = self.coucheModel.getCoucheFromNom(nom_couche_bassins)
            
            if not bassins_versants:
                print(f"La couche des bassins '{nom_couche_bassins}' n'a pas été trouvée.")
                return

            bassins = []
            # --- DEBUT MODIFICATION ---
            bassins_retires = formController.upperList(self.configModel.getFromConfig("bassins_retires", as_list=True))
            # --- FIN MODIFICATION ---
            self.bassins_geom = {}
            
            for feature in bassins_versants.getFeatures():
                bassin = feature[libelle_bassins]
                if bassin not in bassins_retires:
                    bassins.append(bassin)
                    self.bassins_geom[bassin] = feature.geometry()
            
            bassins.sort()
            
            formulaire = container_scenario.findChild(QtWidgets.QFormLayout, 'formulaire_scenario')
            self.dialog.combo_boxes = {}
            
            hauteur_minimum_ligne_formulaire = 25
            for bassin in bassins:
                row_widget = QtWidgets.QWidget()
                row_layout = QtWidgets.QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(2)
                
                label = QtWidgets.QLabel(bassin)
                label.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                
                comboBox = QtWidgets.QComboBox()
                comboBox.setMinimumHeight(hauteur_minimum_ligne_formulaire)
                comboBox.addItems(indices)
                comboBox.setCurrentIndex(comboBox.count() - 1)
                
                row_layout.addWidget(label)
                row_layout.addWidget(comboBox)
                
                comboBox.currentTextChanged.connect(
                    lambda new_text, lib_bassin=label.text(): 
                        formController.handleOccurBassinChanged(new_text, lib_bassin)
                )

                self.dialog.combo_boxes[bassin] = comboBox
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
            project = QgsProject.instance()
            container_sensibilite = self.dialog.findChild(QtWidgets.QWidget, 'container_formulaires').findChild(QtWidgets.QWidget, 'container_sensibilite')
            formulaire = container_sensibilite.findChild(QtWidgets.QFormLayout, 'formulaire_sensibilite')
            
            nom_couche_type = self.configModel.getFromConfig('nom_couche_type')
            if not nom_couche_type:
                nom_couche_type = "type_etendu"
            
            couche_types = project.mapLayersByName(nom_couche_type)
            if not couche_types:
                print(f"La couche des types '{nom_couche_type}' n'a pas été trouvée.")
                return
            
            (types, codes) = self.mapTypes(couche_types[0])
            types = dict(sorted(types.items(), key=lambda item: item[1]))
            
            self.dialog.checkboxes = {}
            
            # --- DEBUT MODIFICATION ---
            types_retires = self.configModel.getFromConfig("types_retires", as_list=True)
            # --- FIN MODIFICATION ---
            
            for id, nom in types.items():
                if codes.get(id) not in types_retires:
                    label = QtWidgets.QLabel(nom)
                    label.setMinimumHeight(25)
                    checkBox = QtWidgets.QCheckBox()
                    checkBox.setMinimumHeight(25)
                    
                    if self.configModel.getFromConfig("sites_coches") == "1":
                        checkBox.setChecked(True)
                    else:
                        checkBox.setChecked(False)
                    
                    self.dialog.checkboxes[id] = checkBox
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
            
        bouton_decocher = self.dialog.findChild(QtWidgets.QPushButton, 'bouton_decocher')
        bouton_cocher = self.dialog.findChild(QtWidgets.QPushButton, 'bouton_cocher')
        bouton_filtre = self.dialog.findChild(QtWidgets.QPushButton, 'bouton_filtre')
        
        bouton_decocher.clicked.connect(lambda: formController.setSensibilite(False))
        bouton_cocher.clicked.connect(lambda: formController.setSensibilite(True))
        bouton_filtre.clicked.connect(lambda: formController.setFiltreSensibilite())