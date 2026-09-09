##Extension de datos para los salarios, obtenidos de pagina web de espn

import io
import re
import time
import unicodedata
import psycopg2
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
from psycopg2.extras import execute_values

DB_CONFIG = {
    "dbname": "proyecto01_bd",
    "user": "postgres",
    "password": "1506",
    "host": "localhost",
    "port": "5432",
}

SEASON_IDS_A_EXTENDER = [2023, 2024, 2025]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

ABREVIATURAS_ESPECIALES = {
    "BKN": "BRK",  # Brooklyn Nets
    "CHA": "CHO",  # Charlotte Hornets
    "PHX": "PHO",  # Phoenix Suns
}


def abreviatura_br(abbr_nba: str) -> str:
    if not abbr_nba:
        return abbr_nba
    abbr_clean = abbr_nba.strip().upper()
    return ABREVIATURAS_ESPECIALES.get(abbr_clean, abbr_clean)


def normaliza_nombre(value: str) -> str:
    if value is None:
        return None
    value = str(value).strip()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def obtener_tabla_salarios(abbr_nba: str, season_id: int) -> pd.DataFrame:
    abbr_br = abreviatura_br(abbr_nba)
    anio_fin_temporada = season_id + 1
    url = f"https://www.basketball-reference.com/teams/{abbr_br}/{anio_fin_temporada}.html"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            print(f"    ERROR status {resp.status_code} en {url}")
            return pd.DataFrame()
    except Exception as e:
        print(f"    Excepción al conectar con {url}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1. Intento directo
    tabla_directa = soup.find("table", id=re.compile(r"salaries"))
    if tabla_directa is not None:
        try:
            return pd.read_html(io.StringIO(str(tabla_directa)))[0]
        except ValueError:
            pass

    # 2. Búsqueda en comentarios HTML
    comentarios = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comentario in comentarios:
        if "salaries" in comentario.lower():
            sub_soup = BeautifulSoup(comentario, "html.parser")
            tabla = sub_soup.find("table", id=re.compile(r"salaries"))
            if tabla is not None:
                try:
                    return pd.read_html(io.StringIO(str(tabla)))[0]
                except ValueError:
                    continue

    print(f"    AVISO: no se encontró tabla de salarios en {url}")
    return pd.DataFrame()


def parsear_salario(valor) -> float:
    if pd.isna(valor):
        return None
    texto = str(valor).replace("$", "").replace(",", "").strip()
    try:
        return float(texto)
    except ValueError:
        return None


def cargar_player_salary_extendido(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT LOWER(TRIM(full_name)), player_id FROM Player;")
    player_map = {normaliza_nombre(nombre): pid for nombre, pid in cursor.fetchall()}

    cursor.execute("SELECT team_id, abbreviation FROM Team;")
    equipos = cursor.fetchall()

    total_insertados = 0
    total_sin_cruce = 0

    for season_id in SEASON_IDS_A_EXTENDER:
        print(f"\n=== Temporada {season_id}-{str(season_id+1)[2:]} ===")

        for team_id, abbr_nba in equipos:
            df = obtener_tabla_salarios(abbr_nba, season_id)
            time.sleep(6)

            if df.empty:
                continue

            col_jugador = df.columns[1] if len(df.columns) > 1 else None
            col_salario = df.columns[2] if len(df.columns) > 2 else None
            if col_jugador is None or col_salario is None:
                print(f"    AVISO: estructura inesperada para {abbr_nba} {season_id}, columnas: {list(df.columns)}")
                continue

            registros = []
            sin_cruce_equipo = 0

            for _, r in df.iterrows():
                nombre = r.get(col_jugador)
                if pd.isna(nombre) or str(nombre).strip().lower() in ("player", "team totals"):
                    continue

                salario = parsear_salario(r.get(col_salario))
                if salario is None:
                    continue

                player_id = player_map.get(normaliza_nombre(nombre))
                if player_id is None:
                    sin_cruce_equipo += 1
                    continue

                registros.append(
                    (
                        player_id,
                        team_id,
                        season_id,
                        None, None, None, None, None, None, None,
                        "basketball_reference_scrape",
                        salario,
                    )
                )

            if registros:
                execute_values(
                    cursor,
                    """INSERT INTO Player_salary (
                        player_id, team_id, season_id, status_player, is_final_season,
                        is_waived, is_on_roster, is_non_guaranteed, is_team_option,
                        is_player_option, contract_detail_type, value_salary
                    ) VALUES %s
                    ON CONFLICT (player_id, team_id, season_id) DO NOTHING""",
                    registros,        
                )
                conn.commit()

            print(f"  {abbr_nba}: {len(registros)} insertados, {sin_cruce_equipo} sin cruce")
            total_insertados += len(registros)
            total_sin_cruce += sin_cruce_equipo

    cursor.close()
    print(f"\nTOTAL: {total_insertados} insertados, {total_sin_cruce} sin cruce en toda la extensión.")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cargar_player_salary_extendido(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()