import configparser
import os

class ConfigModel():
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'etc', 'Config.cfg')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
        else:
            print(f"Le fichier de configuration {self.config_path} n'a pas été trouvé. Il sera créé à la sauvegarde.")

    def getFromConfig(self, key, section='Datas', as_list=False):        
        """
        Récupère un élément depuis le fichier de config.
        """
        value = ""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding='utf-8')
            if self.config.has_option(section, key):
                value = self.config.get(section, key)
            else:
                print(f"La clé '{key}' n'a pas été trouvée dans la section '{section}'.")
        else:
            print(f"Le fichier de configuration {self.config_path} n'existe pas.")

        if as_list:
            return value.split(',') if value else []
        else:
            return value

    def setInConfig(self, key, value, section='Datas'):
        """
        Définit ou met à jour une valeur dans le fichier de configuration.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    def save_config(self):
        """
        Sauvegarde les modifications dans le fichier de configuration.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            print(f"Configuration sauvegardée dans {self.config_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier de configuration : {e}")