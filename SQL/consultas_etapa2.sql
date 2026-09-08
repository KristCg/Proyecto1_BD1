/*
    PROYECTO 1 - ETAPA 2
    Consultas

*/


-- 1. Jugador activo más alto y más bajo

SELECT
    CASE
        WHEN p.height = e.altura_maxima THEN 'Más alto'
        ELSE 'Más bajo'
    END AS categoria,
    p.full_name,
    p.height AS altura_pulgadas
FROM player AS p
CROSS JOIN (
    SELECT
        MIN(height) AS altura_minima,
        MAX(height) AS altura_maxima
    FROM player
    WHERE is_active = TRUE
      AND height IS NOT NULL
) AS e
WHERE p.is_active = TRUE
  AND p.height IN (e.altura_minima, e.altura_maxima)
ORDER BY p.height DESC, p.full_name;


-- 2. Promedio de puntos anotados y recibidos por equipo y temporada

SELECT
    s.season_label AS temporada,
    t.full_name AS equipo,
    ROUND(AVG(ts.pts)::numeric, 2) AS promedio_anotados,
    ROUND(AVG(rival.pts)::numeric, 2) AS promedio_recibidos
FROM team_game_stats AS ts
JOIN team_game_stats AS rival
    ON rival.game_id = ts.game_id
   AND rival.team_id <> ts.team_id
JOIN game AS g
    ON g.game_id = ts.game_id
JOIN season AS s
    ON s.season_id = g.season_id
JOIN team AS t
    ON t.team_id = ts.team_id
GROUP BY s.season_id, s.season_label, t.team_id, t.full_name
ORDER BY s.season_id, t.full_name;


-- 3. Top 5 de árbitros en cuyos juegos perdió el equipo visitante

SELECT
    o.official_id,
    o.first_name,
    o.last_name,
    COUNT(DISTINCT g.game_id) AS derrotas_visitante
FROM game_official AS gof
JOIN official AS o
    ON o.official_id = gof.official_id
JOIN game AS g
    ON g.game_id = gof.game_id
JOIN team_game_stats AS visitante
    ON visitante.game_id = g.game_id
   AND visitante.team_id = g.away_team_id
WHERE visitante.wl = 'L'
GROUP BY o.official_id, o.first_name, o.last_name
ORDER BY derrotas_visitante DESC, o.official_id
LIMIT 5;


-- 4A. Equipos con los salarios totales más altos en 2020-21

SELECT
    RANK() OVER (ORDER BY ts.salary_total DESC) AS posicion,
    t.full_name AS equipo,
    ts.salary_total AS salario_total
FROM team_salary AS ts
JOIN team AS t
    ON t.team_id = ts.team_id
JOIN season AS s
    ON s.season_id = ts.season_id
WHERE s.season_label = '2020-21'
ORDER BY posicion
LIMIT 5;


-- 4B. Jugadores mejor pagados y posición salarial de su equipo
-- Criterio de valor: salario individual de la temporada 2020-21.

WITH ranking_equipos AS (
    SELECT
        ts.team_id,
        ts.salary_total,
        RANK() OVER (ORDER BY ts.salary_total DESC) AS posicion_equipo
    FROM team_salary AS ts
    JOIN season AS s
        ON s.season_id = ts.season_id
    WHERE s.season_label = '2020-21'
)
SELECT
    RANK() OVER (ORDER BY ps.value_salary DESC) AS posicion_jugador,
    p.full_name AS jugador,
    t.full_name AS equipo,
    ps.value_salary AS salario_jugador,
    re.salary_total AS salario_equipo,
    re.posicion_equipo
FROM player_salary AS ps
JOIN player AS p
    ON p.player_id = ps.player_id
JOIN team AS t
    ON t.team_id = ps.team_id
JOIN season AS s
    ON s.season_id = ps.season_id
JOIN ranking_equipos AS re
    ON re.team_id = ps.team_id
WHERE s.season_label = '2020-21'
ORDER BY posicion_jugador
LIMIT 10;


-- 5. Temporada con más partidos y temporada de mayor duración

WITH resumen AS (
    SELECT
        s.season_id,
        s.season_label,
        COUNT(DISTINCT g.game_id) AS partidos,
        MIN(g.game_date) AS fecha_inicial,
        MAX(g.game_date) AS fecha_final,
        MAX(g.game_date) - MIN(g.game_date) AS duracion_dias
    FROM season AS s
    JOIN game AS g
        ON g.season_id = s.season_id
    GROUP BY s.season_id, s.season_label
)
(SELECT
    'Más partidos' AS criterio,
    season_label,
    partidos,
    fecha_inicial,
    fecha_final,
    duracion_dias
FROM resumen
ORDER BY partidos DESC
LIMIT 1)
UNION ALL
(SELECT
    'Mayor duración' AS criterio,
    season_label,
    partidos,
    fecha_inicial,
    fecha_final,
    duracion_dias
FROM resumen
ORDER BY duracion_dias DESC
LIMIT 1);


-- 6. Mayor diferencia promedio de puntos en 2017-18 y 2018-19

WITH promedios AS (
    SELECT
        g.season_id,
        s.season_label,
        t.team_id,
        t.full_name AS equipo,
        AVG(ts.plus_minus) AS diferencia_promedio
    FROM team_game_stats AS ts
    JOIN game AS g
        ON g.game_id = ts.game_id
    JOIN season AS s
        ON s.season_id = g.season_id
    JOIN team AS t
        ON t.team_id = ts.team_id
    WHERE g.season_id IN (2017, 2018)
    GROUP BY g.season_id, s.season_label, t.team_id, t.full_name
),
ranking AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY season_id
            ORDER BY diferencia_promedio DESC
        ) AS posicion
    FROM promedios
)
SELECT
    season_label AS temporada,
    equipo,
    ROUND(diferencia_promedio::numeric, 2) AS diferencia_promedio
FROM ranking
WHERE posicion = 1
ORDER BY season_id;


-- 7. Jugador más valioso del draft de 2018 en 2020-21
-- Criterio de valor: mayor salario en la última temporada del análisis original.

SELECT
    p.full_name AS jugador,
    t.full_name AS equipo,
    d.pick_overall AS seleccion_draft,
    ps.value_salary AS salario
FROM draft AS d
JOIN player AS p
    ON p.player_id = d.player_id
JOIN player_salary AS ps
    ON ps.player_id = p.player_id
JOIN team AS t
    ON t.team_id = ps.team_id
JOIN season AS s
    ON s.season_id = ps.season_id
WHERE d.year_draft = 2018
  AND s.season_label = '2020-21'
  AND ps.value_salary IS NOT NULL
ORDER BY ps.value_salary DESC
LIMIT 1;


-- 8. Top 5 de estados que más salarios pagaron en 2020-21 y 2021-22

WITH salarios_estado AS (
    SELECT
        ts.season_id,
        s.season_label,
        t.state_name,
        SUM(ts.salary_total) AS salario_total
    FROM team_salary AS ts
    JOIN season AS s
        ON s.season_id = ts.season_id
    JOIN team AS t
        ON t.team_id = ts.team_id
    WHERE s.season_label IN ('2020-21', '2021-22')
    GROUP BY ts.season_id, s.season_label, t.state_name
),
ranking AS (
    SELECT
        *,
        DENSE_RANK() OVER (
            PARTITION BY season_id
            ORDER BY salario_total DESC
        ) AS posicion
    FROM salarios_estado
)
SELECT
    season_label AS temporada,
    posicion,
    state_name AS estado,
    salario_total
FROM ranking
WHERE posicion <= 5
ORDER BY season_id, posicion, state_name;
