CREATE TABLE site_base_rdi_filtre (
    NOM TEXT NOT NULL,
    COMMUNE TEXT NOT NULL,
    TYPE TEXT NOT NULL,
    SECT_INOND TEXT NOT NULL
);

CREATE TABLE status_scenario (
    nom_bassin TEXT NOT NULL,
    indice TEXT NOT NULL
);

CREATE TABLE status_sensibilite (
    id_type INT NOT NULL,
    etat_type INTEGER
);