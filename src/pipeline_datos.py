"""
Entrega 2 · Pipeline de datos de la demo: Bronze -> Silver -> Gold.

Uso (desde la raíz del repositorio):
    python src/pipeline_datos.py

Lee únicamente la muestra de data/bronze/, que está en el repositorio: no hace falta descargar nada.
La muestra se crea aparte con scripts/crear_muestra.py a partir de los ficheros completos.

Fuentes de la muestra:
    - Kaggle "threnjen/board-games-database-from-boardgamegeek": games, mechanics, themes, user_ratings
    - GitHub "beefsack/bgg-ranking-historicals": foto diaria del ranking de BoardGameGeek
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- rutas
ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"

# --------------------------------------------------------------------------- parámetros
MIN_VAL_USUARIO = 10       # Gold: usuarios con >= 10 valoraciones (permite evaluar dejando k fuera)
MIN_VAL_JUEGO = 5          # Gold: juegos con >= 5 valoraciones en la muestra
UMBRAL_POSITIVA = 7.0      # nota >= 7 se marca como valoración positiva
FECHA_RANKING = "2026-11-12"
RANK_SIN_RANKING = 21926   # centinela de threnjen para "sin ranking" (nº de juegos + 1)

# Columnas de games.csv: nombre original -> nombre en Silver/Gold
RENOMBRE_JUEGOS = {
    "BGGId": "bgg_id", "Name": "nombre", "Description": "descripcion", "YearPublished": "anio",
    "GameWeight": "peso", "AvgRating": "nota_media_bgg", "BayesAvgRating": "nota_bayes_bgg",
    "StdDev": "desv_nota_bgg", "MinPlayers": "min_jugadores", "MaxPlayers": "max_jugadores",
    "ComAgeRec": "edad_rec_comunidad", "BestPlayers": "mejor_n_jugadores",
    "NumOwned": "n_propietarios", "NumWant": "n_quieren", "NumWish": "n_deseados",
    "NumWeightVotes": "n_votos_peso", "MfgPlaytime": "duracion_min",
    "ComMinPlaytime": "duracion_min_comunidad", "ComMaxPlaytime": "duracion_max_comunidad",
    "MfgAgeRec": "edad_min", "NumUserRatings": "n_valoraciones_bgg",
    "NumComments": "n_comentarios_bgg", "NumAlternates": "n_nombres_alternativos",
    "NumExpansions": "n_expansiones", "NumImplementations": "n_implementaciones",
    "IsReimplementation": "es_reimplementacion", "Kickstarted": "kickstarter",
    "Rank:boardgame": "ranking_kaggle", "Rank:strategygames": "ranking_kaggle_estrategia",
    "Rank:abstracts": "ranking_kaggle_abstractos", "Rank:familygames": "ranking_kaggle_familiar",
    "Rank:thematic": "ranking_kaggle_tematico", "Rank:cgs": "ranking_kaggle_cartas_colec",
    "Rank:wargames": "ranking_kaggle_guerra", "Rank:partygames": "ranking_kaggle_fiesta",
    "Rank:childrensgames": "ranking_kaggle_infantil",
    "Cat:Thematic": "dom_tematico", "Cat:Strategy": "dom_estrategia", "Cat:War": "dom_guerra",
    "Cat:Family": "dom_familiar", "Cat:CGS": "dom_cartas_colec", "Cat:Abstract": "dom_abstracto",
    "Cat:Party": "dom_fiesta", "Cat:Childrens": "dom_infantil",
}
DESCARTADAS = {  # columnas que no pasan a Silver y por qué
    "ImagePath": "URL de imagen: no aporta al modelo y la imagen tiene derechos de BGG",
    "LanguageEase": "escala no documentada (suma de votos, máx. 1757), no interpretable",
    "Family": "texto libre, nulo en ~70 % de los juegos del fichero completo",
}
# Valor 0 = dato no informado en la fuente (no es un valor real)
CERO_ES_NULO = ["anio", "peso", "min_jugadores", "max_jugadores", "duracion_min",
                "duracion_min_comunidad", "duracion_max_comunidad", "edad_min", "mejor_n_jugadores"]


# --------------------------------------------------------------------------- utilidades
def leer_texto(ruta: Path) -> pd.DataFrame:
    """Lee todo como texto y sin convertir 'null', 'NA'... en nulos."""
    return pd.read_csv(ruta, dtype=str, keep_default_na=False)


def guardar(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)


# --------------------------------------------------------------------------- SILVER
def _ancho_a_largo(df: pd.DataFrame, columna: str) -> tuple[pd.DataFrame, dict]:
    """Pasa una tabla 0/1 (una columna por mecánica o tema) a pares (bgg_id, valor)."""
    largo = df.melt(id_vars="BGGId", var_name=columna, value_name="v")
    valores = set(largo["v"].unique())
    assert valores <= {"0", "1"}, f"valores inesperados en {columna}: {valores}"
    largo = largo[largo["v"] == "1"]
    largo = pd.DataFrame({"bgg_id": largo["BGGId"].astype(int), columna: largo[columna].str.strip()})
    stats = {"juegos_sin_ninguno": int((~df["BGGId"].astype(int).isin(largo["bgg_id"])).sum()),
             "valores_distintos": int(largo[columna].nunique()), "pares": len(largo)}
    return largo.sort_values(["bgg_id", columna]).reset_index(drop=True), stats


def _rango_buenos(texto: str) -> tuple[float, float]:
    """GoodPlayers llega como texto "['2', '3', '4']": se extraen el mínimo y el máximo."""
    try:
        lista = [int(x) for x in ast.literal_eval(texto)]
    except (ValueError, SyntaxError):
        lista = []
    return (min(lista), max(lista)) if lista else (np.nan, np.nan)


def silver() -> dict:
    print("[Silver] Tipos, nulos, duplicados y normalización")
    inf: dict = {}

    # --- Juegos
    g = leer_texto(BRONZE / "games.csv")
    inf_j = {"filas_bronze": len(g), "bgg_id_duplicados": int(g["BGGId"].duplicated().sum())}
    g = g.drop_duplicates("BGGId")
    rangos = g["GoodPlayers"].map(_rango_buenos)
    g["buenos_jugadores_min"] = [r[0] for r in rangos]
    g["buenos_jugadores_max"] = [r[1] for r in rangos]
    g = g.drop(columns=list(DESCARTADAS) + ["GoodPlayers"]).rename(columns=RENOMBRE_JUEGOS)
    texto = ["nombre", "descripcion"]
    numericas = [c for c in g.columns if c not in texto]
    g[numericas] = g[numericas].replace("", np.nan).apply(pd.to_numeric, errors="coerce")
    for c in texto:
        g[c] = g[c].str.strip().replace("", np.nan)

    nulos = {}
    for c in CERO_ES_NULO:
        mascara = g[c] == 0
        nulos[c] = int(mascara.sum())
        g.loc[mascara, c] = np.nan
    for c in [c for c in g.columns if c.startswith("ranking_kaggle")]:
        mascara = g[c] == RANK_SIN_RANKING
        nulos[c] = int(mascara.sum())
        g.loc[mascara, c] = np.nan
    incoherente = g["max_jugadores"] < g["min_jugadores"]
    g.loc[incoherente, ["min_jugadores", "max_jugadores"]] = np.nan
    inf_j.update({
        "columnas_descartadas": DESCARTADAS,
        "ceros_o_centinelas_a_nulo": {k: v for k, v in nulos.items() if v},
        "max_menor_que_min_a_nulo": int(incoherente.sum()),
        "anio_negativo_conservado": int((g["anio"] < 0).sum()),
        "descripcion": "texto ya preprocesado en la fuente (minúsculas, sin stopwords, lematizado)",
        "filas_silver": len(g),
    })
    enteras = [c for c in numericas if c not in
               ["peso", "nota_media_bgg", "nota_bayes_bgg", "desv_nota_bgg", "edad_rec_comunidad"]]
    g[enteras] = g[enteras].round().astype("Int64")
    guardar(g, SILVER / "juegos.csv")
    inf["juegos"] = inf_j
    ids_juegos = set(g["bgg_id"])

    # --- Mecánicas y temas: formato ancho (0/1) -> pares juego-valor
    for fichero, col in [("mechanics.csv", "mecanica"), ("themes.csv", "tema")]:
        largo, stats = _ancho_a_largo(leer_texto(BRONZE / fichero), col)
        assert set(largo["bgg_id"]) <= ids_juegos
        guardar(largo, SILVER / f"juego_{col}.csv")
        inf[f"juego_{col}"] = stats

    # --- Valoraciones
    v = pd.read_csv(BRONZE / "user_ratings.csv", dtype={"BGGId": int, "Rating": float, "UserRef": int})
    inf_v = {"filas_bronze": len(v)}
    fuera = ~v["Rating"].between(1, 10)          # la escala de BGG es 1-10
    inf_v["nota_fuera_de_escala_eliminadas"] = int(fuera.sum())
    v = v[~fuera]
    claves = ["UserRef", "BGGId"]
    dup = v.duplicated(claves, keep=False)
    inf_v["pares_usuario_juego_repetidos"] = int(v[dup].drop_duplicates(claves).shape[0])
    inf_v["filas_implicadas"] = int(dup.sum())
    rango = v[dup].groupby(claves)["Rating"].agg(lambda s: s.max() - s.min())
    inf_v["diferencia_mediana_entre_notas_repetidas"] = float(rango.median()) if len(rango) else 0.0
    # Sin fecha no se sabe cuál es la última: se toma la media de las notas repetidas
    v = v.groupby(claves, as_index=False)["Rating"].mean()
    v["Rating"] = v["Rating"].round(5)
    huerfanas = ~v["BGGId"].isin(ids_juegos)
    inf_v["sin_juego_en_catalogo_eliminadas"] = int(huerfanas.sum())
    v = v[~huerfanas].rename(columns={"UserRef": "user_id", "BGGId": "bgg_id", "Rating": "nota"})
    inf_v["filas_silver"] = len(v)
    guardar(v, SILVER / "valoraciones.csv")
    inf["valoraciones"] = inf_v

    # --- Ranking actual (foto diaria)
    r = leer_texto(BRONZE / f"bgg_ranks_{FECHA_RANKING}.csv")
    inf_r = {"filas_bronze": len(r)}
    r = r.drop_duplicates()                       # filas repetidas por la paginación del scraper
    inf_r["filas_identicas_eliminadas"] = inf_r["filas_bronze"] - len(r)
    n = len(r)
    r = r.drop_duplicates("ID", keep="first")     # mismo juego dos veces con datos distintos
    inf_r["id_repetido_eliminadas"] = n - len(r)
    r = r.drop(columns=["URL", "Thumbnail"]).rename(columns={
        "ID": "bgg_id", "Name": "nombre_actual", "Year": "anio_actual", "Rank": "ranking_actual",
        "Average": "nota_media_actual", "Bayes average": "nota_bayes_actual",
        "Users rated": "n_votos_actual"})
    for c in ["bgg_id", "anio_actual", "ranking_actual", "n_votos_actual"]:
        r[c] = pd.to_numeric(r[c]).astype("Int64")
    for c in ["nota_media_actual", "nota_bayes_actual"]:
        r[c] = pd.to_numeric(r[c])
    r["fecha_ranking"] = FECHA_RANKING
    inf_r["filas_silver"] = len(r)
    guardar(r, SILVER / "ranking_actual.csv")
    inf["ranking_actual"] = inf_r

    for k, d in inf.items():
        print(f"  {k}: {d.get('filas_silver', d.get('pares'))} filas")
    return inf


# --------------------------------------------------------------------------- GOLD
def gold(inf_silver: dict | None = None) -> None:
    print("[Gold] Tablas finales para ML y para MySQL")
    j = pd.read_csv(SILVER / "juegos.csv")
    v = pd.read_csv(SILVER / "valoraciones.csv")
    r = pd.read_csv(SILVER / "ranking_actual.csv")
    jm = pd.read_csv(SILVER / "juego_mecanica.csv")
    jt = pd.read_csv(SILVER / "juego_tema.csv")
    inf: dict = {"silver": inf_silver or {}}

    # 1) Filtro iterativo: usuarios con >= 10 valoraciones y juegos con >= 5
    n0 = len(v)
    for _ in range(20):
        nu = v.groupby("user_id").size()
        v = v[v["user_id"].isin(nu[nu >= MIN_VAL_USUARIO].index)]
        ng = v.groupby("bgg_id").size()
        v2 = v[v["bgg_id"].isin(ng[ng >= MIN_VAL_JUEGO].index)]
        if len(v2) == len(v):
            break
        v = v2

    # 2) Valoraciones y usuarios (user_id = UserRef de Bronze, para poder rastrear cada fila)
    v["positiva"] = (v["nota"] >= UMBRAL_POSITIVA).astype(int)
    valoraciones = v[["user_id", "bgg_id", "nota", "positiva"]].sort_values(["user_id", "bgg_id"])
    usuarios = (v.groupby("user_id")
                .agg(n_valoraciones=("nota", "size"),
                     nota_media=("nota", "mean"), nota_desv=("nota", "std"))
                .round(4).reset_index())

    # 3) Juegos: ficha Kaggle + ranking actual (join por bgg_id)
    juegos = j[j["bgg_id"].isin(valoraciones["bgg_id"])].merge(r, on="bgg_id", how="left")
    con_ranking = juegos["ranking_actual"].notna()
    juegos["crecimiento_votos"] = (juegos["n_votos_actual"] - juegos["n_valoraciones_bgg"]).astype("Int64")
    juegos["n_valoraciones_demo"] = juegos["bgg_id"].map(valoraciones.groupby("bgg_id").size())
    anio_sin_signo = (juegos["anio"] < 0) & (juegos["anio_actual"] == -juegos["anio"])
    renombrados = con_ranking & (juegos["nombre"] != juegos["nombre_actual"])
    columnas = ["bgg_id", "nombre", "anio", "descripcion", "peso", "min_jugadores", "max_jugadores",
                "buenos_jugadores_min", "buenos_jugadores_max", "mejor_n_jugadores", "duracion_min",
                "edad_min", "nota_media_bgg", "nota_bayes_bgg", "desv_nota_bgg", "n_valoraciones_bgg",
                "n_propietarios", "n_deseados", "ranking_kaggle", "kickstarter", "es_reimplementacion"]
    columnas += [c for c in juegos.columns if c.startswith("dom_")]
    columnas += ["ranking_actual", "nota_bayes_actual", "n_votos_actual", "crecimiento_votos",
                 "n_valoraciones_demo"]
    juegos = juegos[columnas].sort_values("bgg_id")
    enteras = [c for c in columnas if juegos[c].dtype == float and c not in
               ["peso", "nota_media_bgg", "nota_bayes_bgg", "desv_nota_bgg", "nota_bayes_actual"]]
    juegos[enteras] = juegos[enteras].astype("Int64")

    # 4) Mecánicas y temas: dimensión + tabla puente (N:M)
    ids = set(juegos["bgg_id"])
    tablas = {}
    for largo, col in [(jm, "mecanica"), (jt, "tema")]:
        largo = largo[largo["bgg_id"].isin(ids)]
        dim = pd.DataFrame({col: sorted(largo[col].unique())})
        dim.insert(0, f"{col}_id", range(1, len(dim) + 1))
        puente = largo.merge(dim, on=col)[["bgg_id", f"{col}_id"]].sort_values(["bgg_id", f"{col}_id"])
        tablas[f"{col}s"], tablas[f"juego_{col}"] = dim, puente

    # 5) Validaciones (claves primarias, claves foráneas, rangos)
    assert valoraciones.duplicated(["user_id", "bgg_id"]).sum() == 0
    assert juegos["bgg_id"].is_unique and usuarios["user_id"].is_unique
    assert set(valoraciones["bgg_id"]) <= ids and set(valoraciones["user_id"]) == set(usuarios["user_id"])
    assert valoraciones["nota"].between(1, 10).all()
    for col in ["mecanica", "tema"]:
        assert set(tablas[f"juego_{col}"]["bgg_id"]) <= ids

    # 6) Guardar
    GOLD.mkdir(parents=True, exist_ok=True)
    guardar(juegos, GOLD / "juegos.csv")
    guardar(valoraciones, GOLD / "valoraciones.csv")
    guardar(usuarios, GOLD / "usuarios.csv")
    for nombre, df in tablas.items():
        guardar(df, GOLD / f"{nombre}.csv")

    nu, ng = valoraciones["user_id"].nunique(), valoraciones["bgg_id"].nunique()
    vpu = valoraciones.groupby("user_id").size()
    inf["gold"] = {
        "valoraciones": len(valoraciones), "filas_eliminadas_por_filtro_minimos": n0 - len(valoraciones),
        "usuarios": nu, "juegos": ng, "densidad_matriz": round(len(valoraciones) / (nu * ng), 4),
        "valoraciones_por_usuario": {"mediana": float(vpu.median()), "p90": float(vpu.quantile(.9)),
                                     "max": int(vpu.max())},
        "nota": {"media": round(valoraciones["nota"].mean(), 3), "desv": round(valoraciones["nota"].std(), 3)},
        "cuota_positivas": round(valoraciones["positiva"].mean(), 3),
        "juegos_con_ranking_actual": int(con_ranking.sum()),
        "juegos_sin_ranking_actual": int((~con_ranking).sum()),
        "juegos_renombrados_desde_kaggle": int(renombrados.sum()),
        "anio_negativo_sin_signo_en_ranking_actual": int(anio_sin_signo.sum()),
        "mecanicas": len(tablas["mecanicas"]), "temas": len(tablas["temas"]),
        "nulos_juegos": {c: int(n) for c, n in juegos.isna().sum().items() if n},
    }
    manifiesto = BRONZE / "_manifiesto.json"
    if manifiesto.exists():
        inf["bronze"] = json.loads(manifiesto.read_text())
    (GOLD / "_informe_calidad.json").write_text(json.dumps(inf, indent=2, ensure_ascii=False))
    print(f"  {len(valoraciones)} valoraciones · {nu} usuarios · {ng} juegos · "
          f"densidad {inf['gold']['densidad_matriz']:.2%}")


# --------------------------------------------------------------------------- main
if __name__ == "__main__":
    gold(silver())
