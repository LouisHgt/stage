SELECT
    sc.nom_bassin as nv0, -- Bassin
    es.commune as nv1,    -- Commune
    te.nom as nv2,        -- Type
    es.NOM as nv3,        -- Nom de site
    es.geometry           -- Inclure la geometry pour que le fichier se forme bien avec qgis:run
FROM
    input1 AS es
INNER JOIN
    input2 AS te ON te.code = es.TYPE             -- Jointure Type <-> Etablissement
INNER JOIN
    input3 AS se ON te.id = se.id_type     -- Jointure Type <-> Statut Sensibilité
INNER JOIN
    input4 AS sc ON sc.nom_bassin = es.SECT_INOND -- Jointure Scénario <-> Etablissement (via bassin)
WHERE
    se.etat_type = 1      -- Filtrer sur le statut de sensibilité
    AND (
        (sc.indice_ret = 'Q10' AND (es.FREQ_INOND = 9 OR es.FREQ_INOND = 10)) OR
        (sc.indice_ret = 'Q20' AND es.FREQ_INOND = 20) OR
        (sc.indice_ret = 'Q30' AND es.FREQ_INOND = 30) OR
        (sc.indice_ret = 'Q50' AND es.FREQ_INOND = 50) OR
        (sc.indice_ret = 'Q100' AND es.FREQ_INOND = 100) OR
        (sc.indice_ret = 'Qex' AND es.FREQ_INOND = 1000) OR
        (sc.indice_ret = 'AZI' AND es.FREQ_INOND = 10000 OR es.FREQ_INOND = 999999)
    )