import os
from qgis.PyQt import uic, QtWidgets #type: ignore
from qgis.core import Qgis #type: ignore

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
        :param config_model: L'instance du ConfigModel pour lire/écrire la configuration.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.iface = parent.iface() # Récupérer l'interface QGIS si besoin

        if not config_model:
            raise ValueError("ConfigDialog nécessite une instance de ConfigModel.")
            
        self.configModel = config_model
        
        # Charger les valeurs actuelles dans les champs
        self.load_settings()
        
        # Connecter le signal `accepted` (clic sur OK) à la méthode de sauvegarde
        self.buttonBox.accepted.connect(self.save_settings)
        # Le bouton Annuler (`rejected`) est déjà connecté pour fermer la fenêtre.

    def load_settings(self):
        """
        Charge les valeurs du fichier de configuration et les affiche dans les LineEdits.
        """
        # Clés du fichier de configuration que nous voulons éditer
        # Note: 'nom_couche_sites_entree' est un exemple, vous devez l'adapter à la clé dans votre .cfg
        self.lineEdit_sites.setText(self.configModel.getFromConfig('nom_couche_sites_entree')) 
        self.lineEdit_bassins.setText(self.configModel.getFromConfig('nom_couche_bassins'))
        self.lineEdit_fond.setText(self.configModel.getFromConfig('nom_couche_fond'))
        self.lineEdit_cours_eau.setText(self.configModel.getFromConfig('nom_couche_cours_d_eau'))
        self.lineEdit_nom_rapport.setText(self.configModel.getFromConfig('nom_rapport'))
        
        print("Paramètres de configuration chargés dans la boîte de dialogue.")

    def save_settings(self):
        """
        Récupère les valeurs des LineEdits et les sauvegarde dans le fichier de configuration.
        """
        print("Tentative de sauvegarde des paramètres...")
        
        # Récupérer les nouvelles valeurs depuis les champs de saisie
        nouvelle_valeur_sites = self.lineEdit_sites.text()
        nouvelle_valeur_bassins = self.lineEdit_bassins.text()
        nouvelle_valeur_fond = self.lineEdit_fond.text()
        nouvelle_valeur_cours_eau = self.lineEdit_cours_eau.text()
        nouvelle_valeur_nom_rapport = self.lineEdit_nom_rapport.text()

        # Mettre à jour les valeurs dans l'objet de configuration en mémoire
        self.configModel.setInConfig('nom_couche_sites_entree', nouvelle_valeur_sites)
        self.configModel.setInConfig('nom_couche_bassins', nouvelle_valeur_bassins)
        self.configModel.setInConfig('nom_couche_fond', nouvelle_valeur_fond)
        self.configModel.setInConfig('nom_couche_cours_d_eau', nouvelle_valeur_cours_eau)
        self.configModel.setInConfig('nom_rapport', nouvelle_valeur_nom_rapport)
        
        # Écrire les changements dans le fichier .cfg
        self.configModel.save_config()

        # Afficher un message de confirmation dans la barre de message de QGIS
        if self.iface:
            self.iface.messageBar().pushMessage(
                "Succès", 
                "La configuration a été mise à jour.",
                level=Qgis.Success,
                duration=3
            )
        
        # La méthode accept() est appelée automatiquement car on est connecté au signal `accepted` du buttonBox.
        # Cela ferme la boîte de dialogue.