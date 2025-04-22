import configparser
import os


class configModel():
    def __init__(self):
        #Emplacement du fichier de config
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'etc', 'Config.cfg')

        #Instance d'un parseur de config
        self.config = configparser.ConfigParser()
    
    def getFromConfig(self, key):        
        """Recupere les elements depuis le fichier de config.

        Retourne :
            liste de strings
        """
        

        #Liste des indices retour
        liste = []
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
            if 'Datas' in self.config and key in self.config['Datas']:
                liste = self.config['Datas'][key].split(',')
            elif 'SQL' in self.config and key in self.config['SQL']:
                liste = self.config['SQL'][key]
            else:
                print("Aucun element de retour trouvé dans le fichier de config.")
        else:
            print("Le fichier de config n'existe pas.")

        return liste
