SELECT
    sc.nom_bassin as nv0, -- Bassin
    UPPER(REPLACE(es.COMMUNE, '-', ' ')) as nv1, -- Commune
    te.nom as nv2,        -- Type
    es.NOM as nv3,        -- Nom de site
    es.geom_s          -- Inclure la geometry pour que le fichier se forme bien avec qgis:run
FROM
    sites AS es
INNER JOIN
    type_etendu AS te ON te.code = es.TYPE             -- Jointure Type <-> Etablissement
INNER JOIN
    status_sensibilite AS se ON te.id = se.id_type     -- Jointure Type <-> Statut Sensibilité
INNER JOIN
    status_scenario AS sc ON sc.nom_bassin = es.SECT_INOND -- Jointure Scénario <-> Etablissement (via bassin)
WHERE
    se.etat_type = 1      -- Filtrer sur le statut de sensibilité
    AND sc.indice <> 'Vide' -- Exclusion des bassins sans indice
    AND (
        (sc.indice = 'Q10' AND es.FREQ_INOND <= 10) OR
        (sc.indice = 'Q20' AND es.FREQ_INOND <= 20) OR
        (sc.indice = 'Q30' AND es.FREQ_INOND <= 30) OR
        (sc.indice = 'Q50' AND es.FREQ_INOND <= 50) OR
        (sc.indice = 'Q100' AND es.FREQ_INOND <= 100) OR
        (sc.indice = 'Qex' AND es.FREQ_INOND <= 1000) OR
        (sc.indice = 'AZI' AND es.FREQ_INOND <= 10000)
    )