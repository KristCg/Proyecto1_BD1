import os
import re
import pandas as pd

CSV_FOLDER_PATH = r"D:\Descargas\Data\Data"
START_YEAR = 2015
END_YEAR = 2025


def read_csv_safe(file_path, **kwargs):
    try:
        df = pd.read_csv(file_path, encoding="utf-8", low_memory=False, **kwargs)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1", low_memory=False, **kwargs)
    df.columns = df.columns.str.lower()
    return df


def extract_year(val):
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip()
    match = re.search(r"(\d{4})", val_str)
    if match:
        year = int(match.group(1))
        if len(val_str) == 5 and val_str.isdigit():
            year = int(val_str[1:])
        return year
    return None


def inspect_csvs():
    if not os.path.exists(CSV_FOLDER_PATH):
        print(f"La ruta '{CSV_FOLDER_PATH}' no existe.")
        return

    files = [f for f in os.listdir(CSV_FOLDER_PATH) if f.endswith(".csv")]

    print(f"=== AUDITORÍA DE CSVs EN: {CSV_FOLDER_PATH} ===\n")

    for file_name in sorted(files):
        file_path = os.path.join(CSV_FOLDER_PATH, file_name)
        df = read_csv_safe(file_path)

        print(f"📄 ARCHIVO: {file_name}")
        print(f"   • Total de filas: {len(df)}")
        print(f"   • Columnas disponibles: {list(df.columns)}")

        # Buscar columnas relacionadas a temporadas o años para validar el filtro
        target_cols = [
            c
            for c in df.columns
            if any(k in c for k in ["year", "season", "date", "slug"])
        ]
        if target_cols:
            print(f"   • Columnas clave detectadas: {target_cols}")

            # Contar filas en rango usando la primera columna clave encontrada
            col_to_check = target_cols[0]
            years = df[col_to_check].apply(extract_year)
            valid_count = years.between(START_YEAR, END_YEAR).sum()
            print(
                f"   • Registros que cumplen el rango ({START_YEAR}-{END_YEAR}) en '{col_to_check}': {valid_count}"
            )

        print("   • Muestra de los primeros 2 registros:")
        # Mostrar solo las primeras 6 columnas para no saturar la terminal
        print(df.iloc[:2, :min(6, len(df.columns))].to_string(index=False))
        print("-" * 70 + "\n")


if __name__ == "__main__":
    inspect_csvs()