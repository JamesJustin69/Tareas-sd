-- Eliminar resultados anteriores
rmf /scripts/resultados.csv;

-- Cargar el CSV con columna 'comuna'
eventos = LOAD '/scripts/eventos_agrupados.csv' USING PigStorage(',') 
          AS (fusion_id:int, tipo:chararray, subtype:chararray, comuna:chararray, pub_time:chararray);

-- Agrupar por comuna
agrupados = GROUP eventos BY comuna;

-- Contar eventos por comuna
conteo = FOREACH agrupados GENERATE group AS comuna, COUNT(eventos) AS total_eventos;

-- Ordenar por total de eventos (descendente)
ordenados = ORDER conteo BY total_eventos DESC;

-- Guardar resultados en CSV
STORE ordenados INTO '/scripts/resultados.csv' USING PigStorage(',');
