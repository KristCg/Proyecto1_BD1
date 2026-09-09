CREATE TABLE Team(
	team_id BIGINT PRIMARY KEY NOT NULL,
	full_name VARCHAR(50),
	abbreviation CHAR(3),
	nickname VARCHAR(30),
	city VARCHAR(30),
	state_name VARCHAR(30),
	year_founded SMALLINT,
	arena VARCHAR(50),
	arena_capacity INT,
    owner_name VARCHAR(30),
    general_manager VARCHAR(30),
    head_coach VARCHAR(30),
    dleague_affiliation VARCHAR(30),
    facebook_url VARCHAR(80),
    instagram_url VARCHAR(80),
    twitter_url VARCHAR(80)
);

ALTER TABLE Team ALTER COLUMN owner_name TYPE VARCHAR(80);
ALTER TABLE Team ALTER COLUMN general_manager TYPE VARCHAR(80);
ALTER TABLE Team ALTER COLUMN head_coach TYPE VARCHAR(60);
ALTER TABLE Team ALTER COLUMN dleague_affiliation TYPE VARCHAR(60);

CREATE TABLE Player(
	player_id INT PRIMARY KEY,
	full_name VARCHAR(50),
	first_name VARCHAR(25),
	last_name VARCHAR(25),
	player_slug VARCHAR(50),
	birthdate DATE,
	school VARCHAR(50),
	country VARCHAR(50),
	last_affiliation VARCHAR(50),
	height SMALLINT,
	weight SMALLINT,
	season_exp SMALLINT,
	position_player VARCHAR(20),
	roster_status VARCHAR(15),
	from_year SMALLINT,
	to_year SMALLINT,
	is_active BOOLEAN,
	draft_year SMALLINT,
	draft_round INT,
	draft_number INT
);

CREATE TABLE Team_history(
	history_id SERIAL PRIMARY KEY,
	team_id INT NOT NULL,
	city VARCHAR(50),
	nickname VARCHAR(30),
	year_founded SMALLINT,
	year_active_till SMALLINT,
	FOREIGN KEY (team_id) REFERENCES Team(team_id)
);

CREATE TABLE Season(
	season_id SMALLINT PRIMARY KEY,
	season_label VARCHAR(10) NOT NULL,
	year_start SMALLINT NOT NULL,
	year_end SMALLINT NOT NULL
);

CREATE TABLE Game(
	game_id VARCHAR(20) PRIMARY KEY,
	season_id SMALLINT NOT NULL,
	game_date DATE NOT NULL,
	game_status_text VARCHAR(30),
	gamecode VARCHAR(30),
	home_team_id INT NOT NULL,
	away_team_id INT NOT NULL,
	attendance INT,
	FOREIGN KEY (season_id) REFERENCES Season(season_id),
	FOREIGN KEY (home_team_id) REFERENCES Team(team_id),
	FOREIGN KEY (away_team_id) REFERENCES Team(team_id)
);

CREATE TABLE Team_game_stats(
	game_id VARCHAR(20) NOT NULL,
	team_id INT NOT NULL,
	is_home BOOLEAN NOT NULL,
	matchup VARCHAR(20),
	wl CHAR(1),
	mins INT,
	fgm SMALLINT,
	fga SMALLINT,
	fg_pct NUMERIC(4,3),
	fg3m SMALLINT,
	fg3a SMALLINT,
	fg3_pct NUMERIC(4,3),
	ftm SMALLINT,
	fta SMALLINT,
	ft_pct NUMERIC(4,3),
	oreb SMALLINT,
	dreb SMALLINT,
	reb SMALLINT,
	ast SMALLINT,
	stl SMALLINT,
	blk SMALLINT,
	tov SMALLINT,
	pf SMALLINT,
	pts SMALLINT,
	plus_minus SMALLINT,
	pts_paint SMALLINT,
	pts_2nd_chance SMALLINT,
	pts_fastbreak SMALLINT,
	pts_off_to SMALLINT,
	largest_lead SMALLINT,
	lead_changes SMALLINT,
	times_tied SMALLINT,
	team_turnovers SMALLINT,
	total_turnovers SMALLINT,
	team_rebounds SMALLINT,
	PRIMARY KEY (game_id, team_id),
	FOREIGN KEY (game_id) REFERENCES Game(game_id),
	FOREIGN KEY (team_id) REFERENCES Team(team_id)
);

CREATE TABLE Official(
	official_id INT PRIMARY KEY,
	first_name VARCHAR(30),
	last_name VARCHAR(30)
);

CREATE TABLE Game_official(
	game_id VARCHAR(20) NOT NULL,
	official_id INT NOT NULL,
	jersey_num VARCHAR(5),
	PRIMARY KEY (game_id, official_id),
	FOREIGN KEY (game_id) REFERENCES Game(game_id),
	FOREIGN KEY (official_id) REFERENCES Official(official_id)
);

CREATE TABLE Draft(
	draft_id SERIAL PRIMARY KEY,
	year_draft SMALLINT NOT NULL,
	round_number SMALLINT,
	round_pick SMALLINT,
	pick_overall SMALLINT,
	player_id INT,
	team_id INT,
	organization_from VARCHAR(60),
	type_organization_from VARCHAR(30),
	location_organization_from VARCHAR(60),
	FOREIGN KEY (player_id) REFERENCES Player(player_id),
	FOREIGN KEY (team_id) REFERENCES Team(team_id)
);

CREATE TABLE Team_salary(
	team_salary_id SERIAL PRIMARY KEY,
	team_id INT NOT NULL,
	season_id SMALLINT NOT NULL,
	salary_total NUMERIC(14,2),
	source_url VARCHAR(120),
	FOREIGN KEY (team_id) REFERENCES Team(team_id),
	FOREIGN KEY (season_id) REFERENCES Season(season_id)
);

CREATE TABLE Player_salary(
	salary_id SERIAL PRIMARY KEY,
	player_id INT NOT NULL,
	team_id INT,
	season_id SMALLINT NOT NULL,
	status_player VARCHAR(20),
	is_final_season BOOLEAN,
	is_waived BOOLEAN,
	is_on_roster BOOLEAN,
	is_non_guaranteed BOOLEAN,
	is_team_option BOOLEAN,
	is_player_option BOOLEAN,
	contract_detail_type VARCHAR(30),
	value_salary NUMERIC(14,2),
	FOREIGN KEY (player_id) REFERENCES Player(player_id),
	FOREIGN KEY (team_id) REFERENCES Team(team_id),
	FOREIGN KEY (season_id) REFERENCES Season(season_id)
);

CREATE TABLE Player_season_stats(
	player_id INT NOT NULL,
	season_id SMALLINT NOT NULL,
	team_id INT NOT NULL,
	jersey VARCHAR(5),
	games_played SMALLINT,
	mins FLOAT,
	pts FLOAT,
	ast FLOAT,
	reb FLOAT,
	oreb FLOAT,
	dreb FLOAT,
	stl FLOAT,
	blk FLOAT,
	tov FLOAT,
	pf FLOAT,
	fg_pct NUMERIC(4,3),
	fg3_pct NUMERIC(4,3),
	ft_pct NUMERIC(4,3),
	all_star_appearances SMALLINT,
	pie NUMERIC(5,3),
	PRIMARY KEY (player_id, season_id, team_id),
	FOREIGN KEY (player_id) REFERENCES Player(player_id),
	FOREIGN KEY (season_id) REFERENCES Season(season_id),
	FOREIGN KEY (team_id) REFERENCES Team(team_id)
);

SELECT 'Team' AS tabla, COUNT(*) FROM Team
UNION ALL SELECT 'Player', COUNT(*) FROM Player
UNION ALL SELECT 'Game', COUNT(*) FROM Game
UNION ALL SELECT 'Team_game_stats', COUNT(*) FROM Team_game_stats
UNION ALL SELECT 'Official', COUNT(*) FROM Official
UNION ALL SELECT 'Game_official', COUNT(*) FROM Game_official
UNION ALL SELECT 'Draft', COUNT(*) FROM Draft
UNION ALL SELECT 'Team_salary', COUNT(*) FROM Team_salary
UNION ALL SELECT 'Player_salary', COUNT(*) FROM Player_salary;

INSERT INTO Team_salary (team_id, season_id, salary_total, source_url)
SELECT team_id, season_id, SUM(value_salary), 'derivado de player_salary'
FROM Player_salary
WHERE team_id IS NOT NULL AND season_id >= 2021
GROUP BY team_id, season_id;

INSERT INTO Team_salary (team_id, season_id, salary_total, source_url)
SELECT 
    team_id, 
    season_id, 
    SUM(value_salary) AS salary_total, 
    'derivado de player_salary' AS source_url
FROM Player_salary
WHERE team_id IS NOT NULL 
  AND season_id = 2021
GROUP BY team_id, season_id;

INSERT INTO Team_salary (team_id, season_id, salary_total, source_url)
SELECT 
    team_id, 
    season_id, 
    SUM(value_salary) AS salary_total, 
    'derivado de player_salary' AS source_url
FROM Player_salary
WHERE team_id IS NOT NULL 
  AND season_id IN (2022, 2023, 2024, 2025)
GROUP BY team_id, season_id;

SELECT season_id, season_label FROM Season ORDER BY season_id ASC;

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

SELECT COUNT(*) AS activos FROM Player WHERE is_active = true;

SELECT LENGTH(game_id) AS longitud, COUNT(*) 
FROM Game 
GROUP BY LENGTH(game_id);

SELECT year_draft, COUNT(*) 
FROM Draft 
WHERE year_draft >= 2015
GROUP BY year_draft 
ORDER BY year_draft;

SELECT 
  (SELECT COUNT(*) FROM Game) AS total_game,
  (SELECT COUNT(*) FROM Team_game_stats) AS total_stats;


SELECT COUNT(*) FROM Player WHERE is_active = false;
SELECT COUNT(*) FROM Player WHERE is_active IS NULL;

SELECT season_id, LENGTH(game_id) AS longitud, COUNT(*)
FROM Game
GROUP BY season_id, LENGTH(game_id)
ORDER BY season_id, longitud;

BEGIN;

DELETE FROM Game_official
WHERE game_id IN (
    SELECT game_id FROM Game
    WHERE LENGTH(game_id) = 10 AND season_id <= 2020
);

DELETE FROM Team_game_stats
WHERE game_id IN (
    SELECT game_id FROM Game
    WHERE LENGTH(game_id) = 10 AND season_id <= 2020
);

DELETE FROM Game
WHERE LENGTH(game_id) = 10 AND season_id <= 2020;

SELECT season_id, LENGTH(game_id), COUNT(*)
FROM Game
GROUP BY season_id, LENGTH(game_id)
ORDER BY season_id;

COMMIT;

SELECT 
  (SELECT COUNT(*) FROM Game) AS total_game,
  (SELECT COUNT(*) FROM Team_game_stats) AS total_stats;

SELECT season_id, COUNT(*) 
FROM Player_salary 
WHERE season_id >= 2021 
GROUP BY season_id 
ORDER BY season_id;

SELECT draft_year, COUNT(*) FROM Player WHERE draft_year >= 2022 GROUP BY draft_year;

SELECT COUNT(*) FROM Player WHERE to_year >= 2023;

ALTER TABLE Player_salary 
ADD CONSTRAINT uq_player_salary_temporada UNIQUE (player_id, team_id, season_id);

SELECT player_id, team_id, season_id, COUNT(*)
FROM Player_salary
GROUP BY player_id, team_id, season_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;


DELETE FROM Player_salary a
USING Player_salary b
WHERE a.salary_id > b.salary_id
  AND a.player_id = b.player_id
  AND a.team_id IS NOT DISTINCT FROM b.team_id
  AND a.season_id = b.season_id;

SELECT player_id, team_id, season_id, COUNT(*)
FROM Player_salary
GROUP BY player_id, team_id, season_id
HAVING COUNT(*) > 1;

ALTER TABLE Player_salary 
ADD CONSTRAINT uq_player_salary_temporada UNIQUE (player_id, team_id, season_id);

SELECT conname FROM pg_constraint WHERE conrelid = 'player_salary'::regclass;

SELECT season_id, COUNT(*) 
FROM Player_salary 
WHERE season_id >= 2021 
GROUP BY season_id 
ORDER BY season_id;


ALTER TABLE Team_salary 
ADD CONSTRAINT uq_team_salary_temporada UNIQUE (team_id, season_id);

SELECT team_id, season_id, COUNT(*) 
FROM Team_salary 
GROUP BY team_id, season_id 
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;

DELETE FROM Team_salary a
USING Team_salary b
WHERE a.team_salary_id > b.team_salary_id
  AND a.team_id = b.team_id
  AND a.season_id = b.season_id;

SELECT COUNT(*) FROM Team_salary WHERE season_id >= 2021;

SELECT COUNT(*) FROM Player_season_stats WHERE pie IS NOT NULL;

SELECT season_id, COUNT(*) 
FROM Game g 
LEFT JOIN Game_official go ON g.game_id = go.game_id 
WHERE go.game_id IS NULL 
GROUP BY season_id
ORDER BY season_id;

DELETE FROM team_salary WHERE season_id IN (2024, 2025);

INSERT INTO team_salary (team_id, season_id, salary_total, source_url)
SELECT team_id, season_id, SUM(value_salary), 'derivado de player_salary (basketball-reference)'
FROM player_salary
WHERE team_id IS NOT NULL AND season_id IN (2024, 2025)
GROUP BY team_id, season_id;

--Queries 7 y 8 de la etapa 2, infromacion adicional


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

-- Calculo y correccion para la temporada 2025/26
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
  AND s.season_label = '2025-26'
  AND ps.value_salary IS NOT NULL
ORDER BY ps.value_salary DESC
LIMIT 1;

SELECT COUNT(*) 
FROM draft d
JOIN player_salary ps ON ps.player_id = d.player_id
JOIN season s ON s.season_id = ps.season_id
WHERE d.year_draft = 2018 AND s.season_label = '2025-26';

SELECT COUNT(*) 
FROM draft d
JOIN player_salary ps ON ps.player_id = d.player_id
JOIN season s ON s.season_id = ps.season_id
WHERE d.year_draft = 2018 AND s.season_label = '2021-22';

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
), ranking AS (
    SELECT
        *,
        DENSE_RANK() OVER (
            PARTITION BY season_id
            ORDER BY salario_total DESC
        ) AS posicion
    FROM salarios_estado
) SELECT
    season_label AS temporada,
    posicion,
    state_name AS estado,
    salario_total
FROM ranking
WHERE posicion <= 5
ORDER BY season_id, posicion, state_name;

--pregunta adicional, respuesta para temporada actual 2025*26

WITH salarios_estado AS (
    SELECT
        ts.season_id,
        s.season_label,
        t.state_name,
        SUM(ts.salary_total) AS salario_total
    FROM team_salary AS ts
    JOIN season AS s ON s.season_id = ts.season_id
    JOIN team AS t ON t.team_id = ts.team_id
    WHERE s.season_label IN ('2024-25', '2025-26')
    GROUP BY ts.season_id, s.season_label, t.state_name
),
ranking AS (
    SELECT *,
        DENSE_RANK() OVER (PARTITION BY season_id ORDER BY salario_total DESC) AS posicion
    FROM salarios_estado
)
SELECT season_label AS temporada, posicion, state_name AS estado, salario_total
FROM ranking
WHERE posicion <= 5
ORDER BY season_id, posicion, state_name;


