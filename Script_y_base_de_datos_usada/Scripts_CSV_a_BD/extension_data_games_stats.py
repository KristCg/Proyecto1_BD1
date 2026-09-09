##Actualizacion de las temporadas desde 2021-22 hasta la 2025-26 oara las estadisticas de la tabla games

import time
import psycopg2
from psycopg2.extras import execute_values
from nba_api.stats.endpoints import leaguegamefinder, boxscoresummaryv2

DB_CONFIG = {
    "dbname": "proyecto01_bd",
    "user": "postgres",
    "password": "1506",
    "host": "localhost",
    "port": "5432",
}

SEASONS_API = {
    2021: "2021-22",
    2022: "2022-23",
    2023: "2023-24",
    2024: "2024-25",
    2025: "2025-26"
}


def cargar_juegos_y_estadisticas(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT team_id FROM Team;")
    valid_team_ids = set(row[0] for row in cursor.fetchall())

    for season_id, season_str in SEASONS_API.items():
        print(f"\n=== Procesando partidos para la temporada {season_str} (ID: {season_id}) ===")

        try:
            game_finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season_str,
                league_id_nullable='00' 
            )
            df_games = game_finder.get_data_frames()[0]
            time.sleep(1.5)
        except Exception as e:
            print(f"Error al obtener partidos para {season_str}: {e}")
            continue

        if df_games.empty:
            continue

        games_dict = {}
        temp_team_stats = []

        for _, row in df_games.iterrows():
            game_id = str(row.get('GAME_ID')).zfill(10)
            team_id = int(row.get('TEAM_ID'))

            if team_id not in valid_team_ids:
                continue

            matchup = str(row.get('MATCHUP', ''))
            is_home = ' vs. ' in matchup or ' vs ' in matchup

            if game_id not in games_dict:
                games_dict[game_id] = {
                    'game_id': game_id,
                    'season_id': season_id,
                    'game_date': row.get('GAME_DATE'),
                    'game_status_text': 'Final',
                    'gamecode': None,
                    'home_team_id': team_id if is_home else None,
                    'away_team_id': None if is_home else team_id,
                    'attendance': None
                }
            else:
                if is_home:
                    games_dict[game_id]['home_team_id'] = team_id
                else:
                    games_dict[game_id]['away_team_id'] = team_id

            raw_wl = row.get('WL')
            wl = str(raw_wl).strip()[0].upper() if raw_wl and str(raw_wl).strip() in ['W', 'L'] else None

            mins = int(row['MIN']) if row.get('MIN') and str(row['MIN']).isdigit() else None
            fgm = int(row['FGM']) if row.get('FGM') is not None else None
            fga = int(row['FGA']) if row.get('FGA') is not None else None
            fg_pct = float(row['FG_PCT']) if row.get('FG_PCT') is not None else None
            fg3m = int(row['FG3M']) if row.get('FG3M') is not None else None
            fg3a = int(row['FG3A']) if row.get('FG3A') is not None else None
            fg3_pct = float(row['FG3_PCT']) if row.get('FG3_PCT') is not None else None
            ftm = int(row['FTM']) if row.get('FTM') is not None else None
            fta = int(row['FTA']) if row.get('FTA') is not None else None
            ft_pct = float(row['FT_PCT']) if row.get('FT_PCT') is not None else None
            oreb = int(row['OREB']) if row.get('OREB') is not None else None
            dreb = int(row['DREB']) if row.get('DREB') is not None else None
            reb = int(row['REB']) if row.get('REB') is not None else None
            ast = int(row['AST']) if row.get('AST') is not None else None
            stl = int(row['STL']) if row.get('STL') is not None else None
            blk = int(row['BLK']) if row.get('BLK') is not None else None
            tov = int(row['TOV']) if row.get('TOV') is not None else None
            pf = int(row['PF']) if row.get('PF') is not None else None
            pts = int(row['PTS']) if row.get('PTS') is not None else None
            plus_minus = int(row['PLUS_MINUS']) if row.get('PLUS_MINUS') is not None and str(row['PLUS_MINUS']).replace('-', '').isdigit() else None

            temp_team_stats.append((
                game_id, team_id, is_home, matchup[:20], wl, mins,
                fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, ftm, fta, ft_pct,
                oreb, dreb, reb, ast, stl, blk, tov, pf, pts, plus_minus,
                None, None, None, None, None, None, None, None, None, None
            ))

        valid_game_ids = set()
        registros_game = []
        for g in games_dict.values():
            if g['home_team_id'] is not None and g['away_team_id'] is not None:
                valid_game_ids.add(g['game_id'])
                registros_game.append((
                    g['game_id'], g['season_id'], g['game_date'], g['game_status_text'],
                    g['gamecode'], g['home_team_id'], g['away_team_id'], g['attendance']
                ))

        seen_keys = set()
        team_stats_list = []
        for stat in temp_team_stats:
            g_id, t_id = stat[0], stat[1]
            if g_id in valid_game_ids and (g_id, t_id) not in seen_keys:
                seen_keys.add((g_id, t_id))
                team_stats_list.append(stat)

        if registros_game:
            query_game = """
                INSERT INTO Game (
                    game_id, season_id, game_date, game_status_text,
                    gamecode, home_team_id, away_team_id, attendance
                ) VALUES %s
                ON CONFLICT (game_id) DO UPDATE SET
                    game_date = EXCLUDED.game_date,
                    home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id;
            """
            execute_values(cursor, query_game, registros_game)

            query_stats = """
                INSERT INTO Team_game_stats (
                    game_id, team_id, is_home, matchup, wl, mins,
                    fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, ftm, fta, ft_pct,
                    oreb, dreb, reb, ast, stl, blk, tov, pf, pts, plus_minus,
                    pts_paint, pts_2nd_chance, pts_fastbreak, pts_off_to,
                    largest_lead, lead_changes, times_tied, team_turnovers,
                    total_turnovers, team_rebounds
                ) VALUES %s
                ON CONFLICT (game_id, team_id) DO UPDATE SET
                    wl = EXCLUDED.wl,
                    pts = EXCLUDED.pts,
                    plus_minus = EXCLUDED.plus_minus;
            """
            execute_values(cursor, query_stats, team_stats_list)
            conn.commit()
            print(f"  Procesados: {len(registros_game)} partidos insertados/actualizados exitosamente.")

    cursor.close()


def cargar_game_officials(conn, limit_games=100):
    
    print("\n=== Poblando tabla Game_official ===")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.game_id 
        FROM Game g 
        LEFT JOIN Game_official go ON g.game_id = go.game_id 
        WHERE go.game_id IS NULL 
        LIMIT %s;
    """, (limit_games,))
    
    pending_games = cursor.fetchall()
    if not pending_games:
        print("No hay partidos pendientes por asignar árbitros.")
        cursor.close()
        return

    registros_officials = []
    
    for (game_id,) in pending_games:
        try:
            summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
            officials_df = summary.officials.get_data_frame()
            time.sleep(1.2)

            for _, row in officials_df.iterrows():
                off_id = int(row['OFFICIAL_ID'])
                jersey_num = str(row['JERSEY_NUM']).strip() if row.get('JERSEY_NUM') else None
                first_name = str(row.get('FIRST_NAME', '')).strip()
                last_name = str(row.get('LAST_NAME', '')).strip()
                full_name = f"{first_name} {last_name}".strip()

                cursor.execute("""
                    INSERT INTO Official (official_id, first_name, last_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (official_id) DO NOTHING;
                """, (off_id, first_name, last_name))
                registros_officials.append((game_id, off_id, jersey_num))

        except Exception as e:
            print(f"Error al procesar árbitros del partido {game_id}: {e}")
            continue

    if registros_officials:
        query_game_official = """
            INSERT INTO Game_official (game_id, official_id, jersey_num)
            VALUES %s
            ON CONFLICT (game_id, official_id) DO NOTHING;
        """
        execute_values(cursor, query_game_official, registros_officials)
        conn.commit()
        print(f"Asignaciones de árbitros completadas: {len(registros_officials)} registros insertados.")

    cursor.close()


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cargar_juegos_y_estadisticas(conn)
        cargar_game_officials(conn, limit_games=2000)
    finally:
        conn.close()


if __name__ == "__main__":
    main()