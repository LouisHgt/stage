# -*- coding: utf-8 -*-
import os
from qgis.PyQt import uic, QtWidgets # type: ignore

# Charger le fichier .ui que vous venez de créer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'config_dialog_base.ui'))

class ConfigDialog(QtWidgets.QDialog, FORM_CLASS):
    """
    Ceci est la classe pour votre nouvelle boîte de dialogue de configuration.
    """
    def __init__(self, parent=None, config_model=None):
        """
        Constructeur.
        
        :param parent: Le widget parent, généralement la fenêtre principale de QGIS.
        :param config_model: Optionnel, si vous avez besoin d'accéder à votre modèle de configuration.
        """
        super().__init__(parent)
        self.setupUi(self)

        # Si vous avez besoin d'accéder à vos modèles, vous pouvez les passer ici
        self.configModel = config_model
        
        # Le QDialogButtonBox est déjà connecté pour fermer la fenêtre via le .ui
        # (slots accept() et reject())
        
        print("Boîte de dialogue de configuration initialisée.")

        # Ici, vous pouvez ajouter la logique pour charger des paramètres
        # depuis self.configModel et les afficher dans des widgets.