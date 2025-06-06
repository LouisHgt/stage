# Plugin QGIS : DDTM_GenerationRapport

Ce plugin pour QGIS permet de générer un rapport (format DOCX) répertoriant les sites considérés à risque en fonction d'un scénario d'inondation sélectionné (période de retour par bassin versant) et d'une classification par type de bâtiment (sensibilité).

## Fonctionnalités

*   **Interface Utilisateur Intuitive:**
    *   Sélection du scénario d'inondation (ex: Q10, Q100, AZI) pour chaque bassin versant pertinent.
    *   Visualisation du bassin séléctionné.
    *   Sélection des types de bâtiments à inclure dans l'analyse via des cases à cocher (gestion de la sensibilité).
*   **Traitement Efficace:**
    *   Utilisation de tâches en arrière-plan (`QgsTask`) pour les opérations potentiellement longues, évitant ainsi de figer l'interface de QGIS.
    *   Génération de couches temporaires (`status_sensibilite.shp`, `status_scenario.shp`) pour stocker les sélections utilisateur.
*   **Sélection des Sites Basée sur SQL:**
    *   Exécution d'une requête SQL personnalisable (située dans `sql/site_retenu.sql`) qui croise les données des sites de base, les informations de type, les scénarios et la sensibilité sélectionnés.
    *   Création d'une couche résultat (`site_retenu.shp` dans le dossier `tmp/`) contenant uniquement les sites répondant aux critères.
*   **Génération de Rapport Automatique:**
    *   Création d'un rapport au format DOCX structuré, listant les sites retenus et organisés hiérarchiquement (par exemple : Bassin Versant > Commune > Type de Site > Nom du Site).
    *   Styles appliqués aux différents niveaux de titres pour une meilleure lisibilité.
*   **Configuration Flexible:**
    *   Utilisation d'un fichier de configuration (`etc/Config.cfg`) pour définir les noms des couches source, les libellés, les indices de retour, les chemins de sortie, etc., permettant une adaptation facile à différents contextes de données sans modifier le code.
*   **Conversion PDF** 
    *   Possibilité de convertir le rapport DOCX en PDF via LibreOffice (le code est présent mais l'activation dépend de la configuration et de l'installation de LibreOffice).

## Prérequis

*   **QGIS:** Version 3.0 ou supérieure.
*   **Bibliothèque Python:** `python-docx` doit être installée dans l'environnement Python de QGIS.
*   **(Optionnel pour PDF)** LibreOffice installé et accessible via la ligne de commande (`soffice`).
*   **Couches de Données Source:** Les couches QGIS nécessaires (Bassins versants, Sites de base avec informations d'inondation, Couche de typologie des sites) doivent être chargées dans le projet QGIS et leurs noms/champs doivent correspondre à ceux spécifiés dans `etc/Config.cfg`.

## Installation

1.  **Installer `python-docx`:**
    *   Ouvrez la console OSGeo4W Shell (si vous êtes sous Windows avec l'installeur OSGeo4W) ou le terminal de votre système.
    *   Exécutez la commande : `pip install python-docx` (vous pourriez avoir besoin d'utiliser `pip3` ou d'adapter la commande selon votre installation Python/QGIS).
2.  **Copier le Plugin:**
    *   Copiez l'intégralité du dossier du plugin (`DDTM_GenerationRapport`) dans le répertoire des plugins de QGIS. Vous pouvez trouver ce répertoire via QGIS : Menu `Extensions` > `Gérer/Installer les extensions...` > Onglet `Paramètres` > Bouton `Ouvrir le répertoire des extensions`.
3.  **Activer le Plugin:**
    *   Lancez QGIS.
    *   Allez dans le menu `Extensions` > `Gérer/Installer les extensions...`.
    *   Trouvez "DDTM-06-GenerationRapport" (nom issu de `metadata.txt`) dans la liste et cochez la case pour l'activer.

## Utilisation

1.  **Préparation:**
    *   Lancez QGIS et chargez votre projet contenant les couches de données source requises (Bassins Versants, Sites, Types).
    *   Assurez-vous que le fichier `etc/Config.cfg` est correctement configuré pour correspondre aux noms exacts de vos couches et des champs pertinents.
2.  **Lancer le Plugin:**
    *   Cliquez sur l'icône du plugin "DDTM Génération Rapport" ![Icône](icon.png) dans la barre d'outils des extensions, ou allez dans le menu `Extensions` > `Génération du rapport PDF` > `génerer un rapport`.
3.  **Configurer le Scénario:**
    *   Dans l'onglet "Scénario d'inondation", utilisez les menus déroulants pour sélectionner la période de retour (ex: Q10, Q100) à appliquer pour chaque bassin versant listé.
4.  **Configurer la Sensibilité:**
    *   Dans l'onglet "Sensibilité des sites", cochez les cases correspondant aux types de bâtiments que vous souhaitez inclure dans le rapport. Décochez ceux à exclure.
5.  **Valider et Générer:**
    *   Précisez si vous voulez la conversion PDF.
    *   Cliquez sur le bouton `Valider`.
    *   Le plugin va maintenant traiter les données en arrière-plan. Une barre de progression s'affichera pour indiquer l'avancement.
6.  **Résultat:**
    *   Une fois le traitement terminé, la fenêtre du plugin se fermera.
    *   Le rapport DOCX (`rapportRDI.docx` par défaut) sera généré dans le dossier `output/` (ou le chemin défini dans `Config.cfg`).
    *   Une copie en PDF de ce rapport se trouve au meme endroit si vous avez coché la case "Générer PDF"
    *   La couche `site_retenu.shp` contenant les géométries et attributs des sites sélectionnés sera créée dans le dossier `tmp/`.

## Configuration (`etc/Config.cfg`)

Ce fichier est crucial pour adapter le plugin à vos données spécifiques.

*   **Section `[Datas]`:**
    *   `nom_couche_bassins`: Nom exact de la couche des bassins versants dans QGIS.
    *   `libelle_couche_bassins`: Nom exact du champ contenant le nom/libellé de chaque bassin.
    *   `nom_couche_type`: Nom de la couche contenant la typologie des sites (doit avoir les champs `id`, `code`, `nom`). Laisser vide pour utiliser "type_etendu" par défaut.
    *   `indices`: Liste des périodes de retour (séparées par des virgules) à proposer dans l'interface.
    *   `nom_couche_status_sensibilite`, `emplacement_couche_status_sensibilite`: Nom et dossier (relatif) pour la couche temporaire de sensibilité.
    *   `nom_couche_status_scenario`, `emplacement_couche_status_scenario`: Nom et dossier (relatif) pour la couche temporaire de scénario.
    *   `nom_couche_site_retenu`, `emplacement_couche_site_retenu`: Nom et dossier (relatif) pour la couche résultat des sites retenus.
    *   `emplacement_rapport`, `nom_rapport`: Dossier (relatif) et nom (sans extension) du fichier DOCX généré.
    *   `convertir_en_pdf`: Flag pour activer la conversion PDF par défaut (elle sera toujours selectionnable
    lors de la validation du formulaire).
*   **Section `[SQL]`:**
    *   `requete_formulaire`: Nom du fichier `.sql` (dans le dossier `sql/`) contenant la requête utilisée pour sélectionner les sites retenus.

**Important:** Modifiez ce fichier avec précaution pour qu'il corresponde exactement à votre environnement de données.

## Architecture

Le plugin est structuré selon le modèle Modèle-Vue-Contrôleur (MVC) :

*   **`model/`**: Contient la logique métier, l'interaction avec les données (couches QGIS, fichier de configuration) et les opérations de traitement (`coucheModel.py`, `configModel.py`).
*   **`view/`**: Gère l'interface utilisateur (la fenêtre de dialogue et ses composants) (`formView.py`, `DDTM_GenerationRapport_dialog_base.ui`).
*   **`controller/`**: Orchestre les interactions entre la vue et le modèle, gère les tâches en arrière-plan et la génération du rapport (`formController.py`, `formulaireTask.py`, `rapportController.py`).

Les fichiers principaux à la racine (`DDTM_GenerationRapport.py`, `__init__.py`, `DDTM_GenerationRapport_dialog.py`) servent à l'initialisation et à l'intégration du plugin dans QGIS.



## Gestion des données

Le plugin traite les données d'entrée (sites à enjeux) dans cet ordre :

* Nettoyage du dossier stockant les fichiers temporaires : `tmp/` (CoucheModel.clearTmpFolder())


* Initialisation de la base de données spacialite :tmp/base_de_donnee (DataBaseModel.init_database())
-> Utilisation de la requete : `sql/init_tables.sql`


* Création de la **table** `type_etendu` (DataBaseModel.create_table_type_etendu())
Cette table stocke la nomenclature des types de sites utilisés pour trier les sites.

Attributs : `id` | `code` | `nom`


* Création des **tables** `status_sensibilite` et `status_scenario` (DatabaseModel.create_table_status_scenario & DatabaseModel.create_table_status_sensibilite)
Ces tables stockent l'état des formulaires au moment de la validation de l'utilisateur.

Attributs status_scenario : `nom_bassin` | `indice`
Attributs status_sensibilite : `id_type` | `etat_type`


* Création de la **table** `sites_bases_sdis_filtre` à partir de la couche `sites_bases_sdis_filtre` 
(CoucheModel.get_sites_from_couche(), DataBaseModel.create_table_sites())
Cette table stocke les sites de la couche `sites_bases_sdis_filtre`

Attributs : `NOM` | `TYPE` | `COMMUNE` | `BASSIN` | `FREQ` | `GEOM`


* Création de la **table** `sites` (DataBaseModel.create_table_sites())
Cette table sert à stocker l'ensembles des sites qu'on souhaite avoir dans notre requete finale.
Pour l'instant, elle est donc une copie de `sites_bases_sdis_filtre`, car c'est notre seule tables d'entrée.
On pourrait par exemple rajouter à `sites` une table `camping` si besoin.

Attributs : `NOM` | `TYPE` | `COMMUNE` | `BASSIN` | `FREQ` | `GEOM`


* Création de la **couche** `sites_retenus` : `tmp/sites_retenus.*`(DataBaseModel.get_sites_retenus(), CoucheModel.createSiteRetenu())
-> Utilisation de la requete : `sql/site_retenu.sql`
Cette couche stocke l'ensemble des sites retenus comme "à risque"
selon le scenario indiqué dans le formulaire

Attributs : `nv0` | `nv1` | `nv2` | `nv3`
`nv0` : Bassin versant
`nv1` : Commune
`nv2` : Type d'établissement
`nv3` : Nom de l'établissement



## Auteur

*   **Louis Huguet** - (lshgt@hotmail.fr)