from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication # type: ignore
from qgis.PyQt.QtGui import QIcon # type: ignore
from qgis.PyQt.QtWidgets import QAction # type: ignore

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .DDTM_GenerationRapport_dialog import DDTM_GenerationRapportDialog
from .config_dialog import ConfigDialog
import os.path
from .model.CoucheModel import CoucheModel
from .model.ConfigModel import ConfigModel
from .controller.RapportController import RapportController
from qgis.core import QgsProject, Qgis # type: ignore


class DDTM_GenerationRapport:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """ ... (la méthode __init__ reste identique) ... """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DDTM_GenerationRapport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Génération du rapport PDF')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        # Instanciation des objets MVC
        self.configModel = ConfigModel()
        self.coucheModel = CoucheModel()
        self.rapportController = RapportController(self.configModel, self.coucheModel)


    def tr(self, message):
        """ ... (la méthode tr reste identique) ... """
        return QCoreApplication.translate('DDTM_GenerationRapport', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """ ... (la méthode add_action reste identique) ... """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """ ... (la méthode initGui reste identique) ... """
        # Action principale (existante)
        icon_path = ':/plugins/DDTM_GenerationRapport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Générer un rapport'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Nouvelle action pour la boîte de dialogue de configuration
        settings_icon_path = ':/plugins/DDTM_GenerationRapport/icon_settings.png' 
        self.add_action(
            settings_icon_path, 
            text=self.tr(u'Configurer le plugin'),
            callback=self.open_config_dialog,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True)

        self.first_start = True


    def unload(self):
        """ ... (la méthode unload reste identique) ... """
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Génération du rapport PDF'),
                action)
            self.iface.removeToolBarIcon(action)
        self.coucheModel.clearTmpFolder()

    def run(self):
        """ ... (la méthode run reste identique) ... """
        try:
            project = QgsProject.instance()
            if not project.fileName():
                self.iface.messageBar().pushMessage(
                    "Action impossible",
                    "Veuillez d'abord ouvrir ou sauvegarder un projet QGIS avant de lancer cet outil.",
                    level=Qgis.Warning,
                    duration=7
                )
                return
            
            self.dlg = DDTM_GenerationRapportDialog(self.coucheModel, self.configModel, self.rapportController, parent=self.iface.mainWindow())
            print("Lancement du plugin DDTM_GenerationRapport")
            self.dlg.show()
            result = self.dlg.exec_()
            
            if result:
                pass
                
        except Exception as e:
            print(f"Une erreur s'est produite dans la méthode run : {e}")
            return
    
    # --- DEBUT MODIFICATION ---
    def open_config_dialog(self):
        """
        Ouvre la boîte de dialogue de configuration.
        """
        try:
            # Créer une instance de votre nouvelle boîte de dialogue en passant iface
            config_dlg = ConfigDialog(
                parent=self.iface.mainWindow(), 
                iface=self.iface,  # <-- ON AJOUTE iface ICI
                config_model=self.configModel
            )
            
            config_dlg.exec_()
            
            print("Boîte de dialogue de configuration fermée.")

        except Exception as e:
            print(f"Une erreur s'est produite en ouvrant la config dialog : {e}")
            return
    # --- FIN MODIFICATION ---