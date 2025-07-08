from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication # type: ignore 
from qgis.PyQt.QtGui import QIcon # type: ignore 
from qgis.PyQt.QtWidgets import QAction # type: ignore 

from .resources import *
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
        """Constructor."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DDTM_GenerationRapport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Génération du rapport PDF')
        self.first_start = None
        
        self.configModel = ConfigModel()
        self.coucheModel = CoucheModel()
        self.rapportController = RapportController(self.configModel, self.coucheModel)

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
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
        """Add a toolbar icon to the toolbar."""
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
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/DDTM_GenerationRapport/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Générer un rapport'),
            callback=self.run,
            parent=self.iface.mainWindow())

        settings_icon_path = ':/plugins/DDTM_GenerationRapport/icon_settings.png' 
        self.add_action(
            settings_icon_path, 
            text=self.tr(u'Configurer le plugin'),
            callback=self.open_config_dialog,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True)

        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Génération du rapport PDF'),
                action)
            self.iface.removeToolBarIcon(action)
        self.coucheModel.clearTmpFolder()

    def run(self):
        """Run method that performs all the real work"""
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
    
    def open_config_dialog(self):
        """
        Ouvre la boîte de dialogue de configuration.
        """
        try:
            config_dlg = ConfigDialog(
                parent=self.iface.mainWindow(), 
                iface=self.iface,
                config_model=self.configModel
            )
            config_dlg.exec_()
            print("Boîte de dialogue de configuration fermée.")
        except Exception as e:
            print(f"Une erreur s'est produite en ouvrant la config dialog : {e}")
            return