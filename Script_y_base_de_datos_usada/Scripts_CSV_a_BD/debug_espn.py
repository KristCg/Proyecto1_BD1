##Conexion para obtener informacion de salarios en la pagina de espn sobre nba

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.espn.com/nba/salaries",
    "Connection": "keep-alive",
}

print("Iniciando solicitud...")

try:
    url = "https://www.basketball-reference.com/contracts/players.html"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    print("Status code:", resp.status_code)
    print("Longitud del HTML:", len(resp.text))
except Exception as e:
    print("ERROR AL CONECTAR:", type(e).__name__, "-", e)

print("Fin del script.")