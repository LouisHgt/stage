import sqlite3
#import spatialite
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
            

            # Création de la base
            with sqlite3.connect(self.emplacement_bd) as conn:
                conn.enable_load_extension(True)
                conn.load_extension('mod_spatialite')
                

                cursor = self.init_spacialite_cursor(conn)
                
                # Initialisation des metadonnées
                cursor.execute("SELECT InitSpatialMetadata(1)")
                
                cursor.executescript(requete)
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la bd {e}")
            raise
    
    
    
    def init_spacialite_cursor(self, connection):
        connection.enable_load_extension(True)
        connection.load_extension('mod_spatialite')
        
        cursor = connection.cursor()
        
        return cursor



    
    
    

    def get_db_file(self):
        # Emplacement de la bd
        emplacement_bd = os.path.join(
            os.path.dirname(__file__),
            '..',
            self.configModel.getFromConfig('emplacement_bd')
        )
        
        return emplacement_bd
          
          
          
          
          
          
          
    def create_table_type_etendu(self):
        """
            Création de la table site_etendu
            table qui fait le lien entre les types de batiments et leur nomenclature associee
            Ex : camp -> camping
        """
        # Récupération de la couche
        couche_type_etendu = self.coucheModel.getCoucheFromNom('type_etendu')
        
        
        # Création d'un dictionnaire dans lequel on va stocker
        # en key le code et en value le type d'etablissement
        types = []
        
        for feature in couche_type_etendu.getFeatures():
            types.append((feature['id'], feature['code'], feature['nom']))

        
        # Requetes
        sql_create = f"""
        DROP TABLE IF EXISTS type_etendu;
        
        CREATE TABLE type_etendu (
            id INTEGER NOT NULL,
            code TEXT NOT NULL,
            nom TEXT NOT NULL
        );
        """
        
        sql_insert = f"INSERT INTO \"type_etendu\" (\"id\", \"code\", \"nom\") VALUES (?, ?, ?)"

        
        # Création de la table type_etendu
        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = self.init_spacialite_cursor(conn)
                
                cursor.executescript(sql_create)
                
                cursor.executemany(sql_insert, types)
        except Exception as e:
            print(f"Erreur lors de la creation de la table type_etendu :{e}")
            raise
          
          
          
          
          
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
                cursor = self.init_spacialite_cursor(conn)
                cursor.executemany(sql_insert, data_to_insert)
            
            return True
        except Exception as e:
            print("Erreur lors de la sauvegarde de status scenario en table")
            print(e)
            raise
            
            
            
            
            
            
            
            
    def create_table_status_sensibilite(self, data_dict):
        """
            Stocke le dictionnaire status scenario dans une table
        """
        
        # Préparation des données à insérer
        data_to_insert = []
        for key, value in data_dict.items():
            data_to_insert.append((key,value))
        
        
        # Construction de la requete SQL
        sql_insert = f"INSERT INTO \"status_sensibilite\" (\"id_type\", \"etat_type\") VALUES (?, ?);"

        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = self.init_spacialite_cursor(conn)
                cursor.executemany(sql_insert, data_to_insert)
            
            return True
        except Exception as e:
            print("Erreur lors de la sauvegarde de status scenario en table")
            print(e)
            raise
            
            
            
            
            
            
            
            
    def create_table_sites(self, nom_table, data):
        """
        Créer une table qui peut servir d'entrée de donées
        Ex: sites_bases_sdis_filtre_rdi
        
        Prend en argument une liste de tuples
        Tuple : NOM, TYPE, COMMUNE, BASSIN, FREQ, GEOM
        """
        
        SRID_GEOMETRIES = 2154
        
        
        
        
        # Création de l'attribut geom, chargement de l'extention spacialite et insertion des données
        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                # Chargement de l'extention   
                cursor = self.init_spacialite_cursor(conn)

                # Création de la table avec geometrie
                sql_drop = f"""
                DROP TABLE IF EXISTS {nom_table};
                """
                
                cursor.execute(sql_drop)
                
                sql_create = f"""
                CREATE TABLE {nom_table} (
                    NOM TEXT NOT NULL,
                    TYPE TEXT NOT NULL,
                    COMMUNE TEXT NOT NULL,
                    SECT_INOND TEXT NOT NULL,
                    FREQ_INOND FLOAT NOT NULL
                );
                """
                
                cursor.execute(sql_create)
                
                
                # Ajout de la colonne geom_s
                sql_select = f"""
                SELECT AddGeometryColumn('{nom_table}', 'geom_s', 2154, 'MULTIPOLYGON', 'XY', 0);
                """
                
                cursor.execute(sql_select)
                
                # Ajout des données
                # Construction de la requete SQL
                sql_insert = f"INSERT INTO \"{nom_table}\" (nom, type, commune, sect_inond, freq_inond, geom_s) VALUES (?,?,?,?,?, ST_GeomFromText(?, 2154));"

                
                cursor.executemany(sql_insert, data)
                

        except Exception as e:
            print(f"Erreur lors de l'insertion des données dans {nom_table}, {e}")       
            raise         
            
            
    
    
    
    
    
    
    
    def convertDataTypes(self, data):
        
        data_to_insert = []
        for tuple in data:
            new_tuple = (
                str(tuple[0]),      # Nom
                str(tuple[1]),      # Type
                str(tuple[2]),      # Commune
                str(tuple[3]),      # Sect_inond
                float(tuple[4]),    # Freq_inond
                str(tuple[5])       # Geom (string)
            )
            
            data_to_insert.append(new_tuple)
        
        return data_to_insert
    
    
    
    
    
    
    
    
    def get_sites(self, liste_tables_entrée):
        """
        Prend une liste de table en entrée et les compiles en une seule
        
        """
        
        if len(liste_tables_entrée) == 0:
            print("Aucun table en entrée !")
            return False
        
        # Requete du tri des sites
        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = self.init_spacialite_cursor(conn)

                # Création de la requete
                sql_select = f"""
                SELECT * 
                FROM {liste_tables_entrée.pop(0)}
                """
                
                
                for table in liste_tables_entrée:
                    sql_select += f"""
                    UNION
                    SELECT *
                    FROM {table}
                    """
                
                sql_select += f"""
                ORDER BY nom
                ;"""
                cursor.execute(sql_select)
                
                data = cursor.fetchall()
                
                return data
                
        except Exception as e:
            print(f"Erreur dans create_table_sites_retenus : {e}")
            raise
        
        
    
    
    
    

    

    
    def get_sites_retenus(self):
        """
            Recuperation des sites retenus
            -> liste finale qui contient les sites qui apparaitrons dans le bilan
            Pour que cette methode soit lancée, il faut qu'il existe les tables:
            status_scenario, status_sensibilite, sites, type_etendu.
        """
        
        
        # Requete
        # Emplacement de la requete
        emplacement_requete = os.path.join(
            os.path.dirname(__file__),
            '..',
            'sql',
            'site_retenu.sql'
            )
        sql_select = self.coucheModel.getSqlQuery(emplacement_requete)
        
        
        # Execution de la requete
        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                cursor = self.init_spacialite_cursor(conn)
                
                cursor.execute(sql_select)
                
                data = cursor.fetchall()
                return data
        except Exception as e:
            print(f"Erreur lors du select des sites_retenus :{e}")
            raise
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def show_database_tables(self, spatialite_ext_path=None, max_rows_per_table=5, max_geom_wkt_length=70):
        """
        Affiche les tables d'une base de données SQLite/SpatiaLite et un aperçu de leur contenu.

        Args:
            db_path (str): Chemin vers le fichier de la base de données (.sqlite).
            spatialite_ext_path (str, optional): Chemin vers l'extension SpatiaLite
                                                (mod_spatialite.dll/.so/.dylib).
                                                Si None, essaie 'mod_spatialite' et
                                                des chemins courants pour OSGeo4W/Linux/macOS.
            max_rows_per_table (int): Nombre maximum de lignes à afficher par table.
            max_geom_wkt_length (int): Longueur maximale pour l'affichage des géométries WKT.
        """

        # Détermination du chemin de l'extension SpatiaLite si non fourni
        if spatialite_ext_path is None:
            potential_paths = ['mod_spatialite'] # Par défaut
            if os.name == 'nt': # Windows
                qgis_prefix_win = os.environ.get('QGIS_PREFIX_PATH')
                if qgis_prefix_win:
                    potential_paths.append(os.path.join(qgis_prefix_win, 'bin', 'mod_spatialite.dll'))
                potential_paths.append('C:/OSGeo4W/bin/mod_spatialite.dll') # Ancien OSGeo4W
                potential_paths.append('C:/OSGeo4W64/bin/mod_spatialite.dll') # Ancien OSGeo4W
            elif os.name == 'posix': # Linux ou macOS
                potential_paths.extend([
                    '/usr/lib/x86_64-linux-gnu/mod_spatialite.so', # Linux courant
                    '/usr/local/lib/mod_spatialite.so',          # Linux autre
                    '/usr/local/lib/mod_spatialite.dylib'        # macOS Homebrew
                ])
            
            found_path = None
            for p_path in potential_paths:
                # Le 'mod_spatialite' simple ne peut pas être testé avec os.path.exists
                if p_path == 'mod_spatialite':
                    # On le garde comme option de dernier recours si les chemins explicites échouent
                    continue
                if os.path.exists(p_path):
                    found_path = p_path
                    break
            spatialite_ext_path = found_path if found_path else 'mod_spatialite'
            print(f"Utilisation du chemin SpatiaLite déterminé : '{spatialite_ext_path}'")


        print(f"\n--- Inspection de la base de données : {self.emplacement_bd} ---")
        try:
            with sqlite3.connect(self.emplacement_bd) as conn:
                conn.enable_load_extension(True)
                spatialite_successfully_loaded = False
                try:
                    conn.load_extension(spatialite_ext_path)
                    print(f"Extension SpatiaLite chargée avec succès depuis '{spatialite_ext_path}'.")
                    spatialite_successfully_loaded = True
                except sqlite3.OperationalError as e:
                    print(f"AVERTISSEMENT: Impossible de charger l'extension SpatiaLite depuis '{spatialite_ext_path}': {e}")
                    print("  Les colonnes géométriques pourraient ne pas être interprétées correctement ou les fonctions ST_* ne seront pas disponibles.")

                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Lister les tables utilisateur
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name NOT LIKE 'sqlite_%' 
                    AND name NOT LIKE 'idx_%' 
                    AND name NOT LIKE 'rtree_%' 
                    AND name NOT LIKE 'geom_%'      -- Spécifique à SpatiaLite (vieilles versions)
                    AND name NOT LIKE 'views_%'     -- Spécifique à SpatiaLite
                    AND name NOT LIKE 'virts_%'     -- Spécifique à SpatiaLite
                    AND name NOT LIKE 'ElementaryGeometries' -- Spécifique à SpatiaLite
                    AND name NOT IN ('geometry_columns', 'spatial_ref_sys', 
                                    'spatialite_history', 'spatial_index', 
                                    'vector_layers_statistics', 'vector_layers_auth',
                                    'vector_layers_field_infos', 'vector_layers',
                                    'data_licenses', 'layer_styles', 'metadata',
                                    'KNN'); -- Tables de métadonnées SpatiaLite
                """)
                tables = [row['name'] for row in cursor.fetchall()]

                if not tables:
                    print("Aucune table utilisateur trouvée dans la base de données.")
                    return

                print(f"\nTables utilisateur trouvées : {', '.join(tables)}")

                # Obtenir les informations sur les colonnes géométriques si SpatiaLite est chargé
                geometry_columns_info = {}
                if spatialite_successfully_loaded:
                    try:
                        cursor.execute("SELECT f_table_name, f_geometry_column, type, srid FROM geometry_columns;")
                        for row in cursor.fetchall():
                            table_name_lower = row['f_table_name'].lower()
                            geom_col_name_lower = row['f_geometry_column'].lower()
                            if table_name_lower not in geometry_columns_info:
                                geometry_columns_info[table_name_lower] = {}
                            geometry_columns_info[table_name_lower][geom_col_name_lower] = {
                                'type': row['type'],
                                'srid': row['srid']
                            }
                    except sqlite3.OperationalError:
                        print("  (Note: La table 'geometry_columns' n'a pas été trouvée. Affichage standard des géométries.)")
                        # On peut considérer SpatiaLite comme non chargé pour la suite du formatage
                        # spatialite_successfully_loaded = False # Optionnel: forcer l'affichage standard

                # Parcourir chaque table
                for table_name in tables:
                    print(f"\n--- Contenu de la table : \"{table_name}\" (max {max_rows_per_table} lignes) ---")

                    cursor.execute(f"PRAGMA table_info(\"{table_name}\");")
                    columns_pragma = cursor.fetchall()
                    if not columns_pragma:
                        print(f"  Impossible d'obtenir les informations des colonnes pour la table \"{table_name}\".")
                        continue

                    column_names = [col_info['name'] for col_info in columns_pragma]
                    select_expressions = []
                    table_geom_cols = geometry_columns_info.get(table_name.lower(), {})

                    for col_name in column_names:
                        quoted_col_name = f"\"{col_name}\"" # Toujours mettre les noms de colonnes entre guillemets
                        if spatialite_successfully_loaded and col_name.lower() in table_geom_cols:
                            select_expressions.append(f"ST_AsText({quoted_col_name}) AS \"{col_name}_wkt\"")
                            select_expressions.append(f"ST_IsValid({quoted_col_name}) AS \"{col_name}_is_valid\"")
                            select_expressions.append(f"ST_GeometryType({quoted_col_name}) AS \"{col_name}_type\"")
                        else:
                            select_expressions.append(quoted_col_name)
                    
                    select_clause = ", ".join(select_expressions)
                    query = f"SELECT {select_clause} FROM \"{table_name}\" LIMIT {max_rows_per_table};"

                    try:
                        cursor.execute(query)
                        rows = cursor.fetchall()

                        if not rows:
                            print(f"  La table \"{table_name}\" est vide.")
                            continue

                        header = [desc[0] for desc in cursor.description]
                        print("  " + " | ".join(header))
                        print("  " + "-+-".join(["-" * len(h) for h in header]))

                        for row_data in rows:
                            display_values = []
                            for col_header_name in header:
                                value = row_data[col_header_name]
                                if isinstance(value, str) and col_header_name.lower().endswith("_wkt") and len(value) > max_geom_wkt_length:
                                    display_values.append(f"{value[:max_geom_wkt_length]}...")
                                elif isinstance(value, bytes):
                                    display_values.append(f"<BLOB {len(value)} bytes>")
                                else:
                                    display_values.append(str(value))
                            print("  " + " | ".join(display_values))

                        cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
                        total_rows = cursor.fetchone()[0]
                        if total_rows > max_rows_per_table:
                            print(f"  ... et {total_rows - max_rows_per_table} autre(s) ligne(s) (total: {total_rows}).")

                    except sqlite3.OperationalError as e:
                        print(f"  Erreur lors de la lecture de la table \"{table_name}\": {e}")
                        # Si ST_AsText a échoué parce que SpatiaLite n'est pas vraiment chargé/initialisé
                        if "no such function: ST_AsText" in str(e) or "no such function: st_astext" in str(e).lower():
                            print("    Fonction SpatiaLite non trouvée. Tentative d'affichage standard des colonnes...")
                            plain_select_clause = ", ".join([f"\"{cn}\"" for cn in column_names]) # Sélectionner toutes les colonnes telles quelles
                            plain_query = f"SELECT {plain_select_clause} FROM \"{table_name}\" LIMIT {max_rows_per_table};"
                            try:
                                cursor.execute(plain_query)
                                rows_fallback = cursor.fetchall()
                                if not rows_fallback: continue # Déjà géré

                                header_fallback = [desc[0] for desc in cursor.description]
                                print("  " + " | ".join(header_fallback)) # Réafficher l'en-tête simple
                                print("  " + "-+-".join(["-" * len(h) for h in header_fallback]))

                                for row_fallback_data in rows_fallback:
                                    display_values_fallback = []
                                    for col_fallback_name in header_fallback:
                                        value_fallback = row_fallback_data[col_fallback_name]
                                        if isinstance(value_fallback, bytes):
                                            # Tenter de décoder en UTF-8 si c'est du texte stocké en BLOB, sinon afficher comme BLOB
                                            try:
                                                str_val = value_fallback.decode('utf-8')
                                                if len(str_val) > max_geom_wkt_length : str_val = str_val[:max_geom_wkt_length] + "..."
                                                display_values_fallback.append(str_val)
                                            except UnicodeDecodeError:
                                                display_values_fallback.append(f"<BLOB {len(value_fallback)} bytes>")
                                        else:
                                            str_val = str(value_fallback)
                                            if len(str_val) > max_geom_wkt_length : str_val = str_val[:max_geom_wkt_length] + "..."
                                            display_values_fallback.append(str_val)
                                    print("  " + " | ".join(display_values_fallback))
                            except sqlite3.Error as e_fallback:
                                print(f"    Échec de la tentative d'affichage standard : {e_fallback}")


        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de l'accès à la base de données '{self.emplacement_bd}': {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de l'inspection de la base de données: {e}")