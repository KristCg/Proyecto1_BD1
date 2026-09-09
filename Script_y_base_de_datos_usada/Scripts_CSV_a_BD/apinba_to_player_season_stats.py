##SCRIPT WUE EXTRAE DEL API NBA LAS ESTADISTICAS POR TEMPORADAS DE LOS JUGADORES 

import time
import unicodedata
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from nba_api.stats.endpoints import leaguedashplayerstats

DB_CONFIG = {
    "dbname": "proyecto01_bd",
    "user": "postgres",
    "password": "1506",
    "host": "localhost",
    "port": "5432",
}

SEASONS_API = {
    2015: "2015-16",
    2016: "2016-17",
    2017: "2017-18",
    2018: "2018-19",
    2019: "2019-20",
    2020: "2020-21",
    2021: "2021-22",
    2022: "2022-23",
    2023: "2023-24",
    2024: "2024-25",
    2025: "2025-26"
}


def normaliza_nombre(value: str) -> str:
    if value is None:
        return None
    value = str(value).strip()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    return value.lower()


def cargar_player_season_stats_api(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT LOWER(TRIM(full_name)), player_id FROM Player;")
    player_map = {normaliza_nombre(nombre): pid for nombre, pid in cursor.fetchall()}

    cursor.execute("SELECT UPPER(TRIM(abbreviation)), team_id FROM Team;")
    team_map = {abbr: tid for abbr, tid in cursor.fetchall()}

    for season_id, season_str in SEASONS_API.items():
        print(f"\n=== Consultando API NBA para la temporada {season_str} (ID: {season_id}) ===")

        try:
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season_str,
                season_type_all_star='Regular Season'
            )
            df = stats.get_data_frames()[0]
            time.sleep(2)
        except Exception as e:
            print(f"Error al obtener datos de la API para {season_str}: {e}")
            continue

        registros = []
        sin_cruce_player = 0
        sin_cruce_team = 0

        for _, row in df.iterrows():
            nombre_jugador = normaliza_nombre(row.get('PLAYER_NAME'))
            player_id = player_map.get(nombre_jugador)

            if not player_id:
                sin_cruce_player += 1
                continue

            team_abbr = str(row.get('TEAM_ABBREVIATION')).strip().upper()
            team_id = team_map.get(team_abbr)

            if not team_id:
                sin_cruce_team += 1
                continue

            gp = int(row['GP']) if pd.notna(row.get('GP')) else None
            mins = float(row['MIN']) if pd.notna(row.get('MIN')) else None
            pts = float(row['PTS']) if pd.notna(row.get('PTS')) else None
            ast = float(row['AST']) if pd.notna(row.get('AST')) else None
            reb = float(row['REB']) if pd.notna(row.get('REB')) else None
            oreb = float(row['OREB']) if pd.notna(row.get('OREB')) else None
            dreb = float(row['DREB']) if pd.notna(row.get('DREB')) else None
            stl = float(row['STL']) if pd.notna(row.get('STL')) else None
            blk = float(row['BLK']) if pd.notna(row.get('BLK')) else None
            tov = float(row['TOV']) if pd.notna(row.get('TOV')) else None
            pf = float(row['PF']) if pd.notna(row.get('PF')) else None

            fg_pct = float(row['FG_PCT']) if pd.notna(row.get('FG_PCT')) else None
            fg3_pct = float(row['FG3_PCT']) if pd.notna(row.get('FG3_PCT')) else None
            ft_pct = float(row['FT_PCT']) if pd.notna(row.get('FT_PCT')) else None

            jersey = None
            all_star_appearances = None
            pie = None

            registros.append((
                player_id,
                season_id,
                team_id,
                jersey,
                gp,
                mins,
                pts,
                ast,
                reb,
                oreb,
                dreb,
                stl,
                blk,
                tov,
                pf,
                fg_pct,
                fg3_pct,
                ft_pct,
                all_star_appearances,
                pie
            ))

        if registros:
            query = """
                INSERT INTO Player_season_stats (
                    player_id, season_id, team_id, jersey, games_played,
                    mins, pts, ast, reb, oreb, dreb, stl, blk, tov, pf,
                    fg_pct, fg3_pct, ft_pct, all_star_appearances, pie
                ) VALUES %s
                ON CONFLICT (player_id, season_id, team_id) 
                DO UPDATE SET
                    games_played = EXCLUDED.games_played,
                    mins = EXCLUDED.mins,
                    pts = EXCLUDED.pts,
                    ast = EXCLUDED.ast,
                    reb = EXCLUDED.reb,
                    oreb = EXCLUDED.oreb,
                    dreb = EXCLUDED.dreb,
                    stl = EXCLUDED.stl,
                    blk = EXCLUDED.blk,
                    tov = EXCLUDED.tov,
                    pf = EXCLUDED.pf,
                    fg_pct = EXCLUDED.fg_pct,
                    fg3_pct = EXCLUDED.fg3_pct,
                    ft_pct = EXCLUDED.ft_pct;
            """
            execute_values(cursor, query, registros)
            conn.commit()
            print(f"  Procesados: {len(registros)} insertados/actualizados. (Sin cruce jugador: {sin_cruce_player}, equipo: {sin_cruce_team})")

    cursor.close()


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cargar_player_season_stats_api(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()