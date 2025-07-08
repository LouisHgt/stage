import os
from qgis.PyQt import uic, QtWidgets # type: ignore
from qgis.core import Qgis # type: ignore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'config_dialog_base.ui'))

class ConfigDialog(QtWidgets.QDialog, FORM_CLASS):
    """
    Boîte de dialogue pour la configuration du plugin.
    """
    def __init__(self, parent=None, iface=None, config_model=None):
        """
        Constructeur.
        
        :param parent: Le widget parent, généralement la fenêtre principale de QGIS.
        :param iface: L'interface QGIS pour afficher des messages.
        :param config_model: L'instance du ConfigModel pour lire/écrire la configuration.
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.iface = iface
        self.configModel = config_model

        if not self.iface:
            raise ValueError("ConfigDialog nécessite une instance de l'interface QGIS (iface).")
        if not self.configModel:
            raise ValueError("ConfigDialog nécessite une instance de ConfigModel.")
            
        self.load_settings()
        
        self.buttonBox.accepted.connect(self.save_settings)

    def load_settings(self):
        """
        Charge les valeurs du fichier de configuration et les affiche dans les LineEdits.
        """
        self.lineEdit_sites.setText(self.configModel.getFromConfig('nom_couche_sites')) 
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
        
        nouvelle_valeur_sites = self.lineEdit_sites.text()
        nouvelle_valeur_bassins = self.lineEdit_bassins.text()
        nouvelle_valeur_fond = self.lineEdit_fond.text()
        nouvelle_valeur_cours_eau = self.lineEdit_cours_eau.text()
        nouvelle_valeur_nom_rapport = self.lineEdit_nom_rapport.text()

        self.configModel.setInConfig('nom_couche_sites_entree', nouvelle_valeur_sites)
        self.configModel.setInConfig('nom_couche_bassins', nouvelle_valeur_bassins)
        self.configModel.setInConfig('nom_couche_fond', nouvelle_valeur_fond)
        self.configModel.setInConfig('nom_couche_cours_d_eau', nouvelle_valeur_cours_eau)
        self.configModel.setInConfig('nom_rapport', nouvelle_valeur_nom_rapport)
        
        self.configModel.save_config()

        self.iface.messageBar().pushMessage(
            "Succès", 
            "La configuration a été mise à jour.",
            level=Qgis.Success,
            duration=3
        )