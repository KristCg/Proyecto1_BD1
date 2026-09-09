## Script base para evaluar los CSV del proyecto de NBA antes de diseñar el DDL.

import pandas as pd
from pathlib import Path


def leer_csv(ruta: str) -> pd.DataFrame:

    ruta = Path(ruta)
    try:
        df = pd.read_csv(ruta, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        print("utf-8 falló, probando con latin1...")
        df = pd.read_csv(ruta, encoding="latin1", low_memory=False)
    return df


def resumen_general(df: pd.DataFrame, nombre: str = "dataset"):
    print(f"\n{'='*70}")
    print(f"RESUMEN GENERAL: {nombre}")
    print(f"{'='*70}")
    print(f"Filas: {len(df):,}  |  Columnas: {len(df.columns)}")
    print("\nColumnas y tipo detectado por pandas:")
    print(df.dtypes.to_string())
    print("\nPrimeras 3 filas:")
    print(df.head(3).to_string())


def reporte_nulos(df: pd.DataFrame, nombre: str = "dataset") -> pd.DataFrame:
    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df) * 100).round(2)
    reporte = pd.DataFrame({
        "columna": df.columns,
        "nulos": nulos.values,
        "porcentaje_nulo": porcentaje.values,
        "filas_totales": len(df),
    }).sort_values("porcentaje_nulo", ascending=False)

    print(f"\n{'='*70}")
    print(f"REPORTE DE NULOS: {nombre}")
    print(f"{'='*70}")
    print(reporte.to_string(index=False))
    return reporte


def filtrar_por_temporada(
    df: pd.DataFrame,
    columna_temporada: str,
    temporada_min: str,
    formato: str = "prefijo_year",
) -> pd.DataFrame:
    if formato == "prefijo_year":
       
        anios = df[columna_temporada].astype(str).str.extract(r"(\d{4})$")[0]
        anios = pd.to_numeric(anios, errors="coerce")
        filtrado = df[anios >= int(temporada_min)].copy()
    else:
        raise ValueError("Formato no soportado en este script base; ajústalo según tu columna real.")

    print(f"\nFilas antes del filtro: {len(df):,}")
    print(f"Filas después del filtro (>= {temporada_min}): {len(filtrado):,}")
    return filtrado

def main():
    
    ruta_csv = "Player.csv"          
    
    df = leer_csv(ruta_csv)
    resumen_general(df, nombre=ruta_csv)

    reporte_nulos(df, nombre=f"{ruta_csv} (histórico completo)")

    if columna_temporada in df.columns:
        df_filtrado = filtrar_por_temporada(df, columna_temporada, temporada_min)
        reporte_final = reporte_nulos(df_filtrado, nombre=f"{ruta_csv} (desde {temporada_min})")

        salida = f"reporte_nulos_{Path(ruta_csv).stem}.csv"
        reporte_final.to_csv(salida, index=False)
        print(f"\nReporte exportado a: {salida}")
    else:
        print(f"\nAviso: la columna '{columna_temporada}' no existe en este CSV. "
              f"Revisa el nombre exacto en la lista de columnas de arriba.")


if __name__ == "__main__":
    main()