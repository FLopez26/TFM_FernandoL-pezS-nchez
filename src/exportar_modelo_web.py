"""
Entrega 4 · Exporta el modelo elegido en la entrega 3 para el frontal.

Uso (desde la raíz del repositorio):
    python src/exportar_modelo_web.py

Entrena el item-kNN binario (200 vecinos) con todas las valoraciones del Gold y escribe
frontend/datos_modelo.js con:
    - la ficha básica de cada juego (data/gold/juegos.csv),
    - sus 200 vecinos más parecidos con la similitud coseno,
    - la popularidad (nº de valoraciones positivas), usada cuando el usuario aún no ha marcado juegos.
El frontal (frontend/index.html) solo suma similitudes: no necesita servidor.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ml_recomendador import UMBRAL_POSITIVA, similitud  # noqa: E402  (mismo modelo que la entrega 3)

GOLD = ROOT / "data" / "gold"
SALIDA = ROOT / "frontend" / "datos_modelo.js"
VECINOS = 200  # elegido en validación en la entrega 3


def main() -> None:
    val = pd.read_csv(GOLD / "valoraciones.csv")
    juegos = pd.read_csv(GOLD / "juegos.csv").sort_values("bgg_id").reset_index(drop=True)
    usuarios = np.sort(val["user_id"].unique())
    iu = {u: i for i, u in enumerate(usuarios)}
    ii = {g: i for i, g in enumerate(juegos["bgg_id"])}

    X = np.zeros((len(usuarios), len(juegos)))
    X[val["user_id"].map(iu), val["bgg_id"].map(ii)] = 1.0
    S = similitud(X)
    vecinos = np.argsort(-S, axis=1)[:, :VECINOS]

    pos = val[val["nota"] >= UMBRAL_POSITIVA].groupby("bgg_id").size()
    ficha = []
    for i, j in juegos.iterrows():
        ficha.append({
            "id": int(j.bgg_id), "n": j.nombre, "a": None if pd.isna(j.anio) else int(j.anio),
            "jmin": None if pd.isna(j.min_jugadores) else int(j.min_jugadores),
            "jmax": None if pd.isna(j.max_jugadores) else int(j.max_jugadores),
            "dur": None if pd.isna(j.duracion_min) else int(j.duracion_min),
            "peso": None if pd.isna(j.peso) else round(float(j.peso), 2),
            "rk": None if pd.isna(j.ranking_actual) else int(j.ranking_actual),
            "pop": int(pos.get(j.bgg_id, 0)),
            # vecinos: índices en esta lista y similitud x1000 (entero, para que el fichero pese menos)
            "v": vecinos[i].tolist(), "s": np.round(S[i, vecinos[i]] * 1000).astype(int).tolist(),
        })
    datos = {"modelo": f"item-kNN binario, {VECINOS} vecinos", "usuarios_entrenamiento": len(usuarios),
             "juegos": ficha}
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("// Generado por src/exportar_modelo_web.py. No editar a mano.\n"
                      "window.DATOS_MODELO = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n",
                      encoding="utf-8")
    print(f"{SALIDA.relative_to(ROOT)}: {len(ficha)} juegos, {SALIDA.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
