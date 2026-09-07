SELECT full_name, (select count(*) 
from team_game_stats as victorias 
where victorias.team_id = t.team_id and victorias.wl = 'W') * 100.0 / count(*) as porcentaje_de_victorias
from team_game_stats ts
join team t on ts.team_id = t.team_id
join game g on ts.game_id = g.game_id
where g.season_id <> 2025
group by t.team_id
order by porcentaje_de_victorias desc;

SELECT t.full_name, g.season_id,
(select count(*)
from team_game_stats as victorias
join game as juego_victoria
on juego_victoria.game_id = victorias.game_id
where victorias.team_id = t.team_id
and victorias.wl = 'W'
and juego_victoria.season_id = g.season_id) * 100.0 / count(*) as porcentaje_de_victorias
from team_game_stats ts
join team t
on ts.team_id = t.team_id
join game g
on g.game_id = ts.game_id
where g.season_id <> 2025
group by g.season_id, t.team_id
order by t.full_name, g.season_id;

SELECT resultados.full_name,
max(resultados.porcentaje_de_victorias) as mejor_temporada,
min(resultados.porcentaje_de_victorias) as peor_temporada,
max(resultados.porcentaje_de_victorias) - min(resultados.porcentaje_de_victorias) as diferencia
from (select t.team_id, t.full_name, g.season_id,
(select count(*)
from team_game_stats as victorias
join game as juego_victoria
on juego_victoria.game_id = victorias.game_id
where victorias.team_id = t.team_id
and victorias.wl = 'W'
and juego_victoria.season_id = g.season_id) * 100.0 / count (*) porcentaje_de_victorias
from team_game_stats ts
join team t
on ts.team_id = t.team_id
join game g
on g.game_id = ts.game_id
group by g.season_id, t.team_id)as resultados
group by resultados.team_id, resultados.full_name
order by diferencia;


SELECT t.full_name , sum(ts.blk) as bloqueos ,sum(ts.stl) as robos ,sum(ts.reb) as rebotes, count(*) as partidos
from team t
join team_game_stats ts on t.team_id = ts.team_id
join game g on ts.game_id = g.game_id
where g.season_id = 2024 or g.season_id = 2023 or g.season_id = 2022
group by t.full_name
order by bloqueos desc;

SELECT t.full_name , sum(ts.pts) as puntos ,sum(ts.ast) as asistencias , count(*) as partidos
from team t
join team_game_stats ts on t.team_id = ts.team_id
join game g on ts.game_id = g.game_id
where g.season_id = 2024 or g.season_id = 2023 or g.season_id = 2022
group by t.full_name
order by puntos desc;


SELECT equipo, count(*) as jugadores_jovenes, avg(promedio_puntos) as promedio_puntos,
avg(promedio_asistencias) as promedio_asistencias
from (select p.player_id, t.full_name as equipo, avg(pss.pts) as promedio_puntos, avg(pss.ast) as promedio_asistencias
from player p
join player_season_stats pss on p.player_id = pss.player_id
join team t on t.team_id = ( 
select psss.team_id 
from player_season_stats psss 
where psss.player_id = p.player_id 
order by psss.season_id desc 
limit 1)
where p.birthdate >= '1995-01-01'
group by p.player_id, t.full_name ) as jugadores
group by equipo
order by promedio_puntos desc;

select t.full_name, sum(ps.value_salary) as salario_total
from team t
join player_salary ps on t.team_id = ps.team_id 
where season_id = 2025
and (t.full_name = 'Boston Celtics' 
or t.full_name = 'Oklahoma City Thunder'
or t.full_name = 'Denver Nuggets'
or t.full_name = 'Indiana Pacers'
or t.full_name = 'New York Knicks')
group by t.full_name



