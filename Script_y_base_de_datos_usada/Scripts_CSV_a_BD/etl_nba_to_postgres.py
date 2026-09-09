##lee los CSV del proyecto NBA y carga los datos a PostgreSQL,

import os
import re
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


DB_CONFIG = {
    "dbname": "proyecto01_bd",
    "user": "postgres",
    "password": "1506",
    "host": "localhost",
    "port": "5432",
}

CSV_FOLDER_PATH = r"D:\Descargas\Data\Data"

START_SEASON_YEAR = 2015
END_SEASON_YEAR = 2025


def read_csv_safe(file_path, **kwargs):
    if "low_memory" not in kwargs:
        kwargs["low_memory"] = False

    encodings_to_try = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    for enc in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=enc, **kwargs)
            df.columns = df.columns.str.lower()
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue

    df = pd.read_csv(file_path, encoding="utf-8", errors="replace", **kwargs)
    df.columns = df.columns.str.lower()
    return df


def find_csv(*posibles_nombres):
    
    for nombre in posibles_nombres:
        ruta = os.path.join(CSV_FOLDER_PATH, nombre)
        if os.path.exists(ruta):
            return ruta
    return None


def parse_date(value):
    if pd.isna(value) or value is None or str(value).strip() == "":
        return None
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d")
    except Exception:
        return None


def parse_bool(value):
    if pd.isna(value) or value is None:
        return None
    val_str = str(value).strip().lower()
    if val_str in ["true", "1", "1.0", "t", "yes"]:
        return True
    elif val_str in ["false", "0", "0.0", "f", "no"]:
        return False
    return None


def parse_int(value):
    if pd.isna(value) or value is None:
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_float(value):
    if pd.isna(value) or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_game_id(value):

    if pd.isna(value) or value is None:
        return None
    return str(value).strip()


def parse_wl(value):

    if pd.isna(value) or value is None:
        return None
    val_str = str(value).strip().upper()
    if val_str in ("W", "L"):
        return val_str
    return None


def parse_season_year(value):
    if pd.isna(value) or value is None:
        return None
    val_str = str(value).strip()
    match = re.search(r"(\d{4})", val_str)
    if match:
        year = int(match.group(1))
        if len(val_str) == 5 and val_str.isdigit():
            year = int(val_str[1:])
        return year
    return None


def is_in_season_range(season_val):
    year = parse_season_year(season_val)
    if year is None:
        return False
    return START_SEASON_YEAR <= year <= END_SEASON_YEAR


def normaliza_nombre(value):
    if pd.isna(value) or value is None:
        return None
    return re.sub(r"\s+", " ", str(value).strip().lower())


def clean_str(val):
    if pd.isna(val) or str(val).strip().lower() in ["nan", "none", ""]:
        return None
    return str(val).strip()


def load_team(cursor):
    path_base = find_csv("Team.csv")
    path_attr = find_csv("Team_Attributes.csv", "Team_attributes.csv")

    if path_base is None and path_attr is None:
        print("AVISO: no se encontró Team.csv ni Team_Attributes.csv, se omite Team.")
        return

    df_base = read_csv_safe(path_base) if path_base else pd.DataFrame()
    df_attr = read_csv_safe(path_attr) if path_attr else pd.DataFrame()

    if not df_base.empty and not df_attr.empty:
        id_base = "id" if "id" in df_base.columns else "team_id"
        id_attr = "id" if "id" in df_attr.columns else "team_id"
        df = df_base.merge(
            df_attr, left_on=id_base, right_on=id_attr, how="outer", suffixes=("", "_attr")
        )
    else:
        df = df_base if not df_base.empty else df_attr

    records = []
    for _, r in df.iterrows():
        team_id = parse_int(r.get("id") or r.get("team_id"))
        if team_id is None:
            continue
        records.append(
            (
                team_id,
                r.get("full_name") or r.get("nickname"),
                r.get("abbreviation"),
                r.get("nickname"),
                r.get("city"),
                r.get("state"),
                parse_int(r.get("yearfounded") or r.get("year_founded")),
                r.get("arena"),
                parse_int(r.get("arenacapacity") or r.get("arena_capacity")),
                r.get("owner"),
                r.get("generalmanager") or r.get("general_manager"),
                r.get("headcoach") or r.get("head_coach"),
                r.get("dleagueaffiliation") or r.get("dleague_affiliation"),
                r.get("facebook_website_link") or r.get("facebook_url"),
                r.get("instagram_website_link") or r.get("instagram_url"),
                r.get("twitter_website_link") or r.get("twitter_url"),
            )
        )

    query = """
        INSERT INTO Team (
            team_id, full_name, abbreviation, nickname, city, state_name,
            year_founded, arena, arena_capacity, owner_name, general_manager,
            head_coach, dleague_affiliation, facebook_url, instagram_url, twitter_url
        ) VALUES %s
        ON CONFLICT (team_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Team' cargada exitosamente: {len(records)} registros.")


def load_player(cursor):
    
    path_base = find_csv("Player.csv")
    path_attr = find_csv(
        "Player_atributtes.csv", "Player_Attributes.csv", "Player_attributes.csv"
    )

    if path_base is None and path_attr is None:
        print("AVISO: no se encontró Player.csv ni Player_atributtes.csv, se omite Player.")
        return

    df_base = read_csv_safe(path_base) if path_base else pd.DataFrame()
    df_attr = read_csv_safe(path_attr) if path_attr else pd.DataFrame()

    if not df_base.empty and not df_attr.empty:
        id_base = "id" if "id" in df_base.columns else "player_id"
        id_attr = "id" if "id" in df_attr.columns else "player_id"
        df = df_base.merge(
            df_attr, left_on=id_base, right_on=id_attr, how="outer", suffixes=("", "_attr")
        )
    else:
        df = df_base if not df_base.empty else df_attr

    records = []
    for _, r in df.iterrows():
        player_id = parse_int(r.get("id") or r.get("player_id"))
        if player_id is None:
            continue
        records.append(
            (
                player_id,
                r.get("display_first_last") or r.get("full_name") or r.get("nameplayer"),
                r.get("first_name"),
                r.get("last_name"),
                r.get("player_slug"),
                parse_date(r.get("birthdate")),
                r.get("school"),
                r.get("country"),
                r.get("last_affiliation"),
                parse_int(r.get("height")),
                parse_int(r.get("weight")),
                parse_int(r.get("season_exp")),
                r.get("position"),
                r.get("rosterstatus") or r.get("roster_status"),
                parse_int(r.get("from_year")),
                parse_int(r.get("to_year")),
                parse_bool(r.get("is_active")),
                parse_int(r.get("draft_year")),
                parse_int(r.get("draft_round")),
                parse_int(r.get("draft_number")),
            )
        )

    query = """
        INSERT INTO Player (
            player_id, full_name, first_name, last_name, player_slug, birthdate,
            school, country, last_affiliation, height, weight, season_exp,
            position_player, roster_status, from_year, to_year, is_active,
            draft_year, draft_round, draft_number
        ) VALUES %s
        ON CONFLICT (player_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Player' cargada exitosamente: {len(records)} registros.")


def extract_and_load_seasons(cursor):
    records = [
        (year, f"{year}-{str(year + 1)[-2:]}", year, year + 1)
        for year in range(START_SEASON_YEAR, END_SEASON_YEAR + 1)
    ]
    query = """
        INSERT INTO Season (season_id, season_label, year_start, year_end)
        VALUES %s
        ON CONFLICT (season_id) DO UPDATE
        SET season_label = EXCLUDED.season_label,
            year_start = EXCLUDED.year_start,
            year_end = EXCLUDED.year_end;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Season' cargada ({START_SEASON_YEAR}-{END_SEASON_YEAR}): {len(records)} temporadas.")


def load_game(cursor):
    
    file_path = find_csv("Game.csv")
    if file_path is None:
        print("AVISO: no se encontró Game.csv, se omite Game.")
        return pd.DataFrame()

    df = read_csv_safe(file_path)

    raw_season_col = None
    for candidato in ["season_id", "season"]:
        if candidato in df.columns:
            raw_season_col = candidato
            break

    df["_season_year"] = df[raw_season_col].apply(parse_season_year) if raw_season_col else None
    df_filtrado = df[
        df["_season_year"].notna()
        & (df["_season_year"] >= START_SEASON_YEAR)
        & (df["_season_year"] <= END_SEASON_YEAR)
    ].copy()

    records = []
    for _, r in df_filtrado.iterrows():
        home_id = parse_int(r.get("team_id_home") or r.get("home_team_id"))
        away_id = parse_int(r.get("team_id_away") or r.get("visitor_team_id"))
        game_id = parse_game_id(r.get("game_id"))
        if home_id is None or away_id is None or game_id is None:
            continue

        records.append(
            (
                game_id,
                int(r["_season_year"]),
                parse_date(r.get("game_date") or r.get("game_date_est")),
                r.get("game_status_text"),
                r.get("gamecode"),
                home_id,
                away_id,
                parse_int(r.get("attendance")),
            )
        )

    query = """
        INSERT INTO Game (game_id, season_id, game_date, game_status_text, gamecode, home_team_id, away_team_id, attendance)
        VALUES %s
        ON CONFLICT (game_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Game' cargada (filtrada): {len(records)} juegos insertados.")

    return df_filtrado  


def load_team_game_stats(cursor, df_filtrado):

    if df_filtrado is None or df_filtrado.empty:
        print("AVISO: no hay datos filtrados de Game para generar Team_game_stats.")
        return

    def fila(r, sufijo, team_id, is_home):
        return (
            parse_game_id(r.get("game_id")),
            team_id,
            is_home,
            r.get(f"matchup_{sufijo}"),
            parse_wl(r.get(f"wl_{sufijo}")),
            parse_int(r.get(f"min_{sufijo}")),
            parse_int(r.get(f"fgm_{sufijo}")),
            parse_int(r.get(f"fga_{sufijo}")),
            parse_float(r.get(f"fg_pct_{sufijo}")),
            parse_int(r.get(f"fg3m_{sufijo}")),
            parse_int(r.get(f"fg3a_{sufijo}")),
            parse_float(r.get(f"fg3_pct_{sufijo}")),
            parse_int(r.get(f"ftm_{sufijo}")),
            parse_int(r.get(f"fta_{sufijo}")),
            parse_float(r.get(f"ft_pct_{sufijo}")),
            parse_int(r.get(f"oreb_{sufijo}")),
            parse_int(r.get(f"dreb_{sufijo}")),
            parse_int(r.get(f"reb_{sufijo}")),
            parse_int(r.get(f"ast_{sufijo}")),
            parse_int(r.get(f"stl_{sufijo}")),
            parse_int(r.get(f"blk_{sufijo}")),
            parse_int(r.get(f"tov_{sufijo}")),
            parse_int(r.get(f"pf_{sufijo}")),
            parse_int(r.get(f"pts_{sufijo}")),
            parse_int(r.get(f"plus_minus_{sufijo}")),
            parse_int(r.get(f"pts_paint_{sufijo}")),
            parse_int(r.get(f"pts_2nd_chance_{sufijo}")),
            parse_int(r.get(f"pts_fb_{sufijo}")),
            parse_int(r.get(f"pts_off_to_{sufijo}")),
            parse_int(r.get(f"largest_lead_{sufijo}")),
            parse_int(r.get(f"lead_changes_{sufijo}")),
            parse_int(r.get(f"times_tied_{sufijo}")),
            parse_int(r.get(f"team_turnovers_{sufijo}")),
            parse_int(r.get(f"total_turnovers_{sufijo}")),
            parse_int(r.get(f"team_rebounds_{sufijo}")),
        )

    records = []
    for _, r in df_filtrado.iterrows():
        home_id = parse_int(r.get("team_id_home") or r.get("home_team_id"))
        away_id = parse_int(r.get("team_id_away") or r.get("visitor_team_id"))
        if home_id is None or away_id is None:
            continue
        records.append(fila(r, "home", home_id, True))
        records.append(fila(r, "away", away_id, False))

    query = """
        INSERT INTO Team_game_stats (
            game_id, team_id, is_home, matchup, wl, mins, fgm, fga, fg_pct,
            fg3m, fg3a, fg3_pct, ftm, fta, ft_pct, oreb, dreb, reb, ast, stl,
            blk, tov, pf, pts, plus_minus, pts_paint, pts_2nd_chance,
            pts_fastbreak, pts_off_to, largest_lead, lead_changes, times_tied,
            team_turnovers, total_turnovers, team_rebounds
        ) VALUES %s
        ON CONFLICT (game_id, team_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Team_game_stats' cargada: {len(records)} registros (2 por partido).")


def load_official(cursor):
    file_path = find_csv("Game_Officials.csv")
    if file_path is None:
        print("AVISO: no se encontró Game_Officials.csv, se omite Official.")
        return

    df = read_csv_safe(file_path)
    col_id = "official_id" if "official_id" in df.columns else "oficcioal_id"
    if col_id not in df.columns:
        print(f"AVISO: no se encontró columna de ID de árbitro en {file_path}. "
              f"Columnas disponibles: {list(df.columns)}")
        return

    df_unicos = df.drop_duplicates(subset=[col_id])

    records = []
    for _, r in df_unicos.iterrows():
        official_id = parse_int(r.get(col_id))
        if official_id is None:
            continue
        records.append((official_id, r.get("first_name"), r.get("last_name")))

    query = """
        INSERT INTO Official (official_id, first_name, last_name)
        VALUES %s
        ON CONFLICT (official_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Official' cargada: {len(records)} árbitros únicos.")


def load_game_official(cursor, valid_game_ids):

    file_path = find_csv("Game_Officials.csv")
    if file_path is None:
        print("AVISO: no se encontró Game_Officials.csv, se omite Game_official.")
        return

    df = read_csv_safe(file_path)
    col_id = "official_id" if "official_id" in df.columns else "oficcioal_id"

    records = []
    omitidos = 0
    for _, r in df.iterrows():
        game_id = parse_game_id(r.get("game_id"))
        official_id = parse_int(r.get(col_id))
        if game_id is None or official_id is None:
            continue
        if valid_game_ids is not None and game_id not in valid_game_ids:
            omitidos += 1
            continue
        records.append((game_id, official_id, r.get("jersey_num")))

    query = """
        INSERT INTO Game_official (game_id, official_id, jersey_num)
        VALUES %s
        ON CONFLICT (game_id, official_id) DO NOTHING;
    """
    execute_values(cursor, query, records)
    print(f"Tabla 'Game_official' cargada: {len(records)} registros ({omitidos} omitidos por no estar en el rango de temporadas).")


def load_draft(cursor):
    file_path = find_csv("Draft.csv")
    if file_path is None:
        print("AVISO: no se encontró Draft.csv, se omite Draft.")
        return

    cursor.execute("SELECT player_id FROM Player;")
    valid_player_ids = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT team_id FROM Team;")
    valid_team_ids = {row[0] for row in cursor.fetchall()}

    df = read_csv_safe(file_path)
    records = []
    null_players_count = 0

    for _, r in df.iterrows():
        year_draft = parse_int(r.get("yeardraft") or r.get("year_draft") or r.get("season"))
        if year_draft is None or not (START_SEASON_YEAR <= year_draft <= END_SEASON_YEAR):
            continue

        player_id = parse_int(r.get("idplayer") or r.get("player_id"))
        team_id = parse_int(r.get("idteam") or r.get("team_id"))

        if player_id is None or player_id not in valid_player_ids:
            player_id = None
            null_players_count += 1
        if team_id not in valid_team_ids:
            team_id = None

        records.append(
            (
                year_draft,
                parse_int(r.get("numberround") or r.get("round_number")),
                parse_int(r.get("numberroundpick") or r.get("round_pick")),
                parse_int(r.get("numberpickoverall") or r.get("pick_overall")),
                player_id,
                team_id,
                clean_str(r.get("nameorganizationfrom") or r.get("organization_from")),
                clean_str(r.get("typeorganizationfrom") or r.get("type_organization_from")),
                clean_str(r.get("locationorganizationfrom") or r.get("location_organization_from")),
            )
        )

    if records:
        query = """
            INSERT INTO Draft (
                year_draft, round_number, round_pick, pick_overall, player_id,
                team_id, organization_from, type_organization_from, location_organization_from
            ) VALUES %s;
        """
        execute_values(cursor, query, records)

    print(f"Tabla 'Draft' cargada: {len(records)} registros ({null_players_count} sin player_id resuelto).")


def load_team_salary(cursor):
    file_path = find_csv("Team_Salary.csv")
    if file_path is None:
        print("AVISO: no se encontró Team_Salary.csv, se omite Team_salary.")
        return

    df = read_csv_safe(file_path)

    cursor.execute("SELECT abbreviation, team_id FROM Team;")
    team_map_abbr = {row[0]: row[1] for row in cursor.fetchall() if row[0]}
    cursor.execute("SELECT LOWER(TRIM(full_name)), team_id FROM Team;")
    team_map_nombre = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

    year_cols = [c for c in df.columns if re.search(r"\d{4}", c)]

    records = []
    sin_match = 0
    for _, r in df.iterrows():
        team_id = None
        if "slugteam" in df.columns:
            team_id = team_map_abbr.get(r.get("slugteam"))
        if team_id is None and "nameteam" in df.columns:
            team_id = team_map_nombre.get(normaliza_nombre(r.get("nameteam")))
        if team_id is None:
            sin_match += 1
            continue

        for col in year_cols:
            season_year = parse_season_year(col)
            if season_year is None or not (START_SEASON_YEAR <= season_year <= END_SEASON_YEAR):
                continue
            salary_val = parse_float(r.get(col))
            if salary_val is None:
                continue
            records.append((team_id, season_year, salary_val, r.get("urlteamsalaryhoopshype")))

    query = "INSERT INTO Team_salary (team_id, season_id, salary_total, source_url) VALUES %s;"
    execute_values(cursor, query, records)
    print(f"Tabla 'Team_salary' cargada: {len(records)} registros ({sin_match} filas de equipo sin cruce, ignoradas).")


def load_player_salary(cursor):
    file_path = find_csv("Player_Salary.csv")
    if file_path is None:
        print("AVISO: no se encontró Player_Salary.csv, se omite Player_salary.")
        return

    df = read_csv_safe(file_path)

    cursor.execute("SELECT LOWER(TRIM(full_name)), player_id FROM Player;")
    player_map = {row[0]: row[1] for row in cursor.fetchall() if row[0]}
    cursor.execute("SELECT LOWER(TRIM(full_name)), team_id FROM Team;")
    team_map = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

    records = []
    null_players_count = 0

    for _, r in df.iterrows():
        raw_season = r.get("slugseason")
        if not is_in_season_range(raw_season):
            continue

        p_id = player_map.get(normaliza_nombre(r.get("nameplayer")))
        t_id = team_map.get(normaliza_nombre(r.get("nameteam")))

        if p_id is None:
            null_players_count += 1
            continue 

        records.append(
            (
                p_id,
                t_id,
                parse_season_year(raw_season),
                r.get("statusplayer"),
                parse_bool(r.get("isfinalseason")),
                parse_bool(r.get("iswaived")),
                parse_bool(r.get("isonroster")),
                parse_bool(r.get("isnonguaranteed")),
                parse_bool(r.get("isteamoption")),
                parse_bool(r.get("isplayeroption")),
                r.get("typecontractdetail") or r.get("typecntractdetail"),
                parse_float(r.get("value")),
            )
        )

    if records:
        query = """
            INSERT INTO Player_salary (
                player_id, team_id, season_id, status_player, is_final_season,
                is_waived, is_on_roster, is_non_guaranteed, is_team_option,
                is_player_option, contract_detail_type, value_salary
            ) VALUES %s;
        """
        execute_values(cursor, query, records)

    print(f"Tabla 'Player_salary' cargada: {len(records)} registros ({null_players_count} sin cruce de jugador, ignoradas).")


def load_team_history(cursor):
    file_path = find_csv("Team_History.csv")
    if file_path is None:
        print("AVISO: no se encontró Team_History.csv, se omite Team_history.")
        return
    df = read_csv_safe(file_path)

    records = []
    for _, r in df.iterrows():
        team_id = parse_int(r.get("id") or r.get("team_id"))
        if team_id is None:
            continue
        records.append(
            (
                team_id,
                r.get("city"),
                r.get("nickname"),
                parse_int(r.get("yearfounded")),
                parse_int(r.get("yearactivetill")),
            )
        )

    query = "INSERT INTO Team_history (team_id, city, nickname, year_founded, year_active_till) VALUES %s;"
    execute_values(cursor, query, records)
    print(f"Tabla 'Team_history' cargada: {len(records)} registros.")


def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"Conexión exitosa a PostgreSQL. Cargando y filtrando datos ({START_SEASON_YEAR}-{END_SEASON_YEAR})...")

        load_team(cursor)
        load_player(cursor)
        extract_and_load_seasons(cursor)
        load_team_history(cursor)
        load_official(cursor)

        df_game_filtrado = load_game(cursor)
        load_team_game_stats(cursor, df_game_filtrado)

        valid_game_ids = set(df_game_filtrado["game_id"].apply(parse_game_id)) if not df_game_filtrado.empty else set()
        load_game_official(cursor, valid_game_ids)

        load_draft(cursor)
        load_team_salary(cursor)
        load_player_salary(cursor)

        conn.commit()
        print("\n¡Proceso finalizado con éxito! Todos los registros mapeados e insertados.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n[ERROR] Ocurrió un fallo durante el proceso: {e}")
        raise
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    main()