rmf /scripts/resultados.csv;

eventos = LOAD '/scripts/eventos_agrupados.csv' USING PigStorage(',') 
          AS (fusion_id:int, tipo:chararray, subtype:chararray, comuna:chararray, pub_time:chararray);

agrupados = GROUP eventos BY comuna;

conteo = FOREACH agrupados GENERATE group AS comuna, COUNT(eventos) AS total_eventos;

ordenados = ORDER conteo BY total_eventos DESC;

STORE ordenados INTO '/scripts/resultados.csv' USING PigStorage(',');
