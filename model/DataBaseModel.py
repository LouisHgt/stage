import sqlite3
import os

from ..model.ConfigModel import ConfigModel

class DataBaseModel():
    def __init__(self, coucheModel):
        self.conn = None
        self.cursor = None
        self.configModel = ConfigModel()
        self.coucheModel = coucheModel
        
        # Initialisation de la bd et des tables
        self.init_database()
    
    def init_database(self):
        """
        Initialise la base de donnée
        """
        try:
            # Emplacement de la bd
            emplacement_bd = os.path.join(
                os.path.dirname(__file__),
                '..',
                self.configModel.getFromConfig('emplacement_bd')
            )
            
            # Connexion à la bd
            self.conn = sqlite3.connect(emplacement_bd)
            self.cursor = self.conn.cursor()
            
            # Emplacement de la requete
            emplacement_requete = os.path.join(
                os.path.dirname(__file__),
                '..',
                'sql',
                'init_tables.sql'
                )
            
            # Création de la table site_base_rdi_filtre
            self.cursor.execute(self.coucheModel.getSqlQuery(emplacement_requete))
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la bd {e}")
            