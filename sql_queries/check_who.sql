-- Vérification import OMS
SELECT 
    i.code,
    i.name,
    i.source,
    COUNT(DISTINCT iv.country_id) as pays
FROM indicator i
LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
WHERE i.code IN ('SP.DYN.IMRT.IN', 'SP.DYN.LE00.IN')
GROUP BY i.code, i.name, i.source
ORDER BY i.code;
