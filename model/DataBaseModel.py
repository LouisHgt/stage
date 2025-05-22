import sqlite3
import os

from ..model.ConfigModel import ConfigModel

class DataBaseModel():
    def __init__(self, coucheModel):
        self.configModel = ConfigModel()
        self.coucheModel = coucheModel
        self.emplacement_bd = self.get_db_file()
        
        # Initialisation de la bd et des tables
        self.init_database()
    
    
    
    
    

    def init_database(self):
        """
        Initialise la base de donnée
        """
        try:
            
            # Emplacement de la requete
            emplacement_requete = os.path.join(
                os.path.dirname(__file__),
                '..',
                'sql',
                'init_tables.sql'
                )
            
            requete = self.coucheModel.getSqlQuery(emplacement_requete)
            
            # Création de la table site_base_rdi_filtre
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = conn.cursor()
                cursor.executescript(requete)
            

        except Exception as e:
            print(f"Erreur lors de l'initialisation de la bd {e}")
    
    
    
    
    
    
    

    def get_db_file(self):
        # Emplacement de la bd
        emplacement_bd = os.path.join(
            os.path.dirname(__file__),
            '..',
            self.configModel.getFromConfig('emplacement_bd')
        )
        
        return emplacement_bd
          
          
          
          
          
          
    def create_table_status_scenario(self, data_dict):
        """
            Stocke le dictionnaire status scenario dans une table
        """
        
        # Préparation des données à insérer
        data_to_insert = []
        for key, value in data_dict.items():
            data_to_insert.append((key,value))
        
        
        # Construction de la requete SQL
        sql_insert = f"INSERT INTO \"status_scenario\" (\"nom_bassin\", \"indice\") VALUES (?, ?)"

        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = conn.cursor()
                cursor.executemany(sql_insert, data_to_insert)
            
            return True
        except Exception as e:
            print("Erreur lors de la sauvegarde de status scenario en table")
            print(e)
            
            
            
            
            
    def create_table_status_sensibilite(self, data_dict):
        """
            Stocke le dictionnaire status scenario dans une table
        """
        
        # Préparation des données à insérer
        data_to_insert = []
        for key, value in data_dict.items():
            data_to_insert.append((key,value))
        
        
        # Construction de la requete SQL
        sql_insert = f"INSERT INTO \"status_sensibilite\" (\"id_type\", \"etat_type\") VALUES (?, ?)"

        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = conn.cursor()
                cursor.executemany(sql_insert, data_to_insert)
            
            return True
        except Exception as e:
            print("Erreur lors de la sauvegarde de status scenario en table")
            print(e)
            
            
            
            
    def create_table_sites_base_sdis(self):
        pass