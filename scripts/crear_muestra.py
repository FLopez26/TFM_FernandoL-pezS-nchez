"""
Preparación de la muestra Bronze (se ejecuta una vez, fuera del pipeline).

Toma los ficheros completos de las fuentes y copia en data/bronze/ solo las filas de la muestra demo,
sin cambiar ningún valor. La única diferencia con la fuente es que la columna Username de las
valoraciones se sustituye por un número (UserRef): el nombre real no se sube al repositorio.

Uso (desde la raíz del repositorio, con los ficheros de Kaggle en data/raw/kaggle_threnjen/):
    python scripts/crear_muestra.py

"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KAGGLE_DIR = ROOT / "data" / "raw" / "kaggle_threnjen"
RANKING_DIR = ROOT / "data" / "raw" / "bgg_ranks"
BRONZE = ROOT / "data" / "bronze"

N_JUEGOS = 500              # catálogo demo: los 500 juegos con más valoraciones
FRACCION_USUARIOS = 0.005   # 0,5 % de los usuarios, elegidos por hash del nombre
SEMILLA = "tfm2026"

FECHA_RANKING = "2026-11-12"
URL_RANKING = ("https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/"
               f"master/{FECHA_RANKING}.csv")
URL_KAGGLE = "https://www.kaggle.com/datasets/threnjen/board-games-database-from-boardgamegeek"
FICHEROS_KAGGLE = ["games.csv", "mechanics.csv", "themes.csv", "user_ratings.csv"]


def leer_texto(ruta: Path, **kw) -> pd.DataFrame:
    """Todo como texto y sin convertir 'null', 'NA'... en nulos: los valores se copian tal cual."""
    return pd.read_csv(ruta, dtype=str, keep_default_na=False, **kw)


def hash_muestra(nombre: str) -> float:
    """Número en [0, 1) a partir del nombre y una semilla pública: misma muestra en cada ejecución."""
    h = hashlib.md5(f"{SEMILLA}:{nombre}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0x1_0000_0000


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> None:
    faltan = [f for f in FICHEROS_KAGGLE if not (KAGGLE_DIR / f).exists()]
    if faltan:
        raise SystemExit(f"Faltan en {KAGGLE_DIR}: {faltan}. Instrucciones en data/README.md")
    BRONZE.mkdir(parents=True, exist_ok=True)

    # 1) Catálogo demo: los N juegos con más valoraciones (empates por BGGId)
    games = leer_texto(KAGGLE_DIR / "games.csv")
    orden = games.assign(_n=pd.to_numeric(games["NumUserRatings"]),
                         _id=pd.to_numeric(games["BGGId"]))
    orden = orden.sort_values(["_n", "_id"], ascending=[False, True])
    catalogo = set(orden["BGGId"].head(N_JUEGOS))
    for nombre in ["games.csv", "mechanics.csv", "themes.csv"]:
        df = games if nombre == "games.csv" else leer_texto(KAGGLE_DIR / nombre)
        df[df["BGGId"].isin(catalogo)].to_csv(BRONZE / nombre, index=False)

    # 2) Valoraciones de una fracción de usuarios sobre el catálogo (fichero de 400 MB: por trozos)
    trozos, n_total, n_cat, usuarios_total, n_fuera, n_null = [], 0, 0, set(), 0, 0
    for trozo in leer_texto(KAGGLE_DIR / "user_ratings.csv", chunksize=1_000_000):
        n_total += len(trozo)
        usuarios_total.update(trozo["Username"].unique())
        n_fuera += int((~pd.to_numeric(trozo["Rating"]).between(1, 10)).sum())
        n_null += int((trozo["Username"] == "null").sum())
        trozo = trozo[trozo["BGGId"].isin(catalogo)]
        n_cat += len(trozo)
        elegidos = {u for u in trozo["Username"].unique() if hash_muestra(u) < FRACCION_USUARIOS}
        trozos.append(trozo[trozo["Username"].isin(elegidos)])
    val = pd.concat(trozos, ignore_index=True)
    # Username -> UserRef: número consecutivo según el hash, sin relación con el nombre.
    # La correspondencia no se guarda en ningún sitio.
    nombres = sorted(val["Username"].unique(), key=hash_muestra)
    ref = {u: i + 1 for i, u in enumerate(nombres)}
    val.insert(val.columns.get_loc("Username"), "UserRef", val["Username"].map(ref))
    val = val.drop(columns="Username")
    val.to_csv(BRONZE / "user_ratings.csv", index=False)

    # 3) Ranking actual de BGG: se descarga la foto del día y se copian las filas del catálogo
    destino = RANKING_DIR / f"{FECHA_RANKING}.csv"
    if not destino.exists():
        RANKING_DIR.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL_RANKING, destino)
    rk = leer_texto(destino)
    rk[rk["ID"].isin(catalogo)].to_csv(BRONZE / f"bgg_ranks_{FECHA_RANKING}.csv", index=False)
    rk_u = rk.drop_duplicates("ID").assign(_r=lambda d: pd.to_numeric(d["Rank"]),
                                           _a=lambda d: pd.to_numeric(d["Year"]))
    ausente = ~rk_u["ID"].isin(set(games["BGGId"]))

    manifiesto = {
        "fecha_creacion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuentes": {
            "kaggle_threnjen": {"url": URL_KAGGLE,
                                "sha256": {f: sha256(KAGGLE_DIR / f) for f in FICHEROS_KAGGLE}},
            "ranking_bgg_github": {"url": URL_RANKING, "sha256": sha256(destino)},
        },
        "criterio": {
            "juegos": f"los {N_JUEGOS} con más valoraciones (NumUserRatings), empates por BGGId",
            "usuarios": f"md5('{SEMILLA}:' + Username) < {FRACCION_USUARIOS}",
            "cambio_respecto_a_la_fuente": "Username sustituido por UserRef; el resto, sin cambios",
        },
        "fuente_completa": {
            "juegos": len(games), "valoraciones": n_total, "usuarios": len(usuarios_total),
            "notas_fuera_de_escala": n_fuera, "valoraciones_del_usuario_null": n_null,
            "juegos_en_ranking_actual": len(rk_u),
            "ranking_actual_ausentes_en_kaggle": int(ausente.sum()),
            "ausentes_publicados_desde_2022": int((ausente & (rk_u["_a"] >= 2022)).sum()),
            "top100_actual_ausentes_en_kaggle": int((~rk_u.nsmallest(100, "_r")["ID"]
                                                    .isin(set(games["BGGId"]))).sum()),
            "cuota_valoraciones_en_catalogo_demo": round(n_cat / n_total, 4),
        },
        "muestra": {"juegos": len(catalogo), "usuarios": len(ref), "valoraciones": len(val),
                    "filas_ranking": int(rk["ID"].isin(catalogo).sum())},
    }
    (BRONZE / "_manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False))
    print(f"Muestra Bronze: {len(catalogo)} juegos, {len(ref)} usuarios, {len(val)} valoraciones")


if __name__ == "__main__":
    main()
