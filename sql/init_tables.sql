CREATE TABLE sites_bases_sdis_filtre (
    NOM TEXT NOT NULL,
    TYPE TEXT NOT NULL,
    COMMUNE TEXT NOT NULL,
    SECT_INOND TEXT NOT NULL,
    FREQ_INOND FLOAT NOT NULL
);

SELECT AddGeometryColumn('sites_bases_sdis_filtre', 'geom_s', 2154, 'MULTIPOLYGON', 'XY', 1);
--2154

CREATE TABLE status_scenario (
    nom_bassin TEXT NOT NULL,
    indice TEXT NOT NULL
);

CREATE TABLE status_sensibilite (
    id_type INT NOT NULL,
    etat_type INTEGER
);
