"""
Entrega 3 · Experimento de recomendación (demo) sobre el Gold de la entrega 2.

Uso (desde la raíz del repositorio):
    python src/ml_recomendador.py

Para cada usuario, ordenar los juegos que no ha valorado y devolver un top-10.
Modelos: popularidad (baseline), por contenido (mecánicas + temas) y colaborativo item-kNN.
Validación: se reserva al azar el 20 % de las valoraciones de cada usuario como test. Dentro del
entrenamiento se separa otro 20 % como validación para elegir la variante de item-kNN; el test
solo se usa una vez, para el resultado final.
Resultados en results/entrega03/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "gold"
SALIDA = ROOT / "results" / "entrega03"

SEMILLA = 42
FRAC_TEST = 0.2
K = 10
UMBRAL_POSITIVA = 7.0
N_BOOTSTRAP = 1000


# --------------------------------------------------------------------------- datos
def cargar():
    val = pd.read_csv(GOLD / "valoraciones.csv")
    juegos = pd.read_csv(GOLD / "juegos.csv")
    jm = pd.read_csv(GOLD / "juego_mecanica.csv")
    jt = pd.read_csv(GOLD / "juego_tema.csv")
    return val, juegos, jm, jt


def separar(val: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reserva el 20 % de las valoraciones de cada usuario (sin fechas, no cabe partición temporal)."""
    rng = np.random.default_rng(SEMILLA)
    azar = pd.Series(rng.random(len(val)), index=val.index)
    rango = azar.groupby(val["user_id"]).rank(pct=True)
    test = rango <= FRAC_TEST
    return val[~test].copy(), val[test].copy()


# --------------------------------------------------------------------------- modelos
# Cada modelo devuelve una matriz de puntuaciones usuarios x juegos (más alto = más recomendable).

def popularidad(R_pos: np.ndarray) -> np.ndarray:
    """Baseline: nº de valoraciones positivas de cada juego en entrenamiento, igual para todos."""
    return np.tile(R_pos.sum(axis=0), (R_pos.shape[0], 1)).astype(float)


def contenido(R_cent: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Perfil del usuario = media de los rasgos de sus juegos, ponderada por (nota - su media).
    Puntuación = similitud coseno entre el perfil y los rasgos de cada juego."""
    Fn = F / np.maximum(np.linalg.norm(F, axis=1, keepdims=True), 1e-9)
    perfil = R_cent @ Fn
    perfil /= np.maximum(np.linalg.norm(perfil, axis=1, keepdims=True), 1e-9)
    return perfil @ Fn.T


def similitud(X: np.ndarray) -> np.ndarray:
    """Similitud coseno entre columnas (juegos)."""
    norma = np.maximum(np.linalg.norm(X, axis=0), 1e-9)
    S = (X.T @ X) / np.outer(norma, norma)
    np.fill_diagonal(S, 0)
    return S


def item_knn(X: np.ndarray, vecinos: int) -> np.ndarray:
    """Similitud coseno entre juegos, quedándose con los `vecinos` más parecidos de cada uno.
    Puntuación = suma de similitudes con los juegos del usuario, ponderada por X.
    X puede ser la matriz binaria (ha valorado / no) o la de notas centradas por usuario."""
    S = similitud(X)
    corte = -np.sort(-S, axis=1)[:, vecinos - 1:vecinos]
    S[S < corte] = 0
    return X @ S.T


def matrices(df: pd.DataFrame, iu: dict, ii: dict, forma: tuple) -> dict:
    R = np.zeros(forma)
    R[df["user_id"].map(iu), df["bgg_id"].map(ii)] = df["nota"]
    mascara = R != 0
    medias = R.sum(1) / np.maximum(mascara.sum(1), 1)
    return {"R": R, "mascara": mascara, "binaria": mascara.astype(float),
            "centrada": np.where(mascara, R - medias[:, None], 0),
            "positivas": (R >= UMBRAL_POSITIVA).astype(float)}


def relevantes_de(df: pd.DataFrame, iu: dict, ii: dict, n: int) -> list[set]:
    """Relevantes = juegos reservados con nota >= 7."""
    rel = [set() for _ in range(n)]
    for u, g in df.loc[df["nota"] >= UMBRAL_POSITIVA, ["user_id", "bgg_id"]].itertuples(index=False):
        rel[iu[u]].add(ii[g])
    return rel


# --------------------------------------------------------------------------- evaluación
def evaluar(puntos: np.ndarray, R_train: np.ndarray, relevantes: list[set], pop_rank: np.ndarray):
    """Top-K sobre juegos no valorados en entrenamiento. Devuelve métricas por usuario y los tops."""
    puntos = np.where(R_train != 0, -np.inf, puntos)
    top = np.argsort(-puntos, axis=1)[:, :K]
    descuento = 1 / np.log2(np.arange(2, K + 2))
    filas = []
    for u, rel in enumerate(relevantes):
        if not rel:
            continue
        acierto = np.array([i in rel for i in top[u]])
        ideal = descuento[: min(len(rel), K)].sum()
        filas.append({"u": u, "precision": acierto.mean(), "recall": acierto.sum() / len(rel),
                      "ndcg": (acierto * descuento).sum() / ideal,
                      "pop_media_rank": pop_rank[top[u]].mean()})
    return pd.DataFrame(filas), top


def ic_bootstrap(x: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(SEMILLA)
    medias = rng.choice(x, (N_BOOTSTRAP, len(x))).mean(axis=1)
    return float(np.percentile(medias, 2.5)), float(np.percentile(medias, 97.5))


# --------------------------------------------------------------------------- main
def main() -> None:
    val, juegos, jm, jt = cargar()
    train, test = separar(val)

    usuarios = np.sort(val["user_id"].unique())
    items = np.sort(juegos["bgg_id"].unique())
    iu = {u: i for i, u in enumerate(usuarios)}
    ii = {g: i for i, g in enumerate(items)}

    forma = (len(usuarios), len(items))

    # 1) Elección de la variante de item-kNN en validación (dentro del entrenamiento)
    sub, valid = separar(train)
    Mv = matrices(sub, iu, ii, forma)
    rel_v = relevantes_de(valid, iu, ii, len(usuarios))
    rank_v = pd.Series(-Mv["positivas"].sum(0)).rank(method="min").to_numpy()
    grid = []
    for variante in ["binaria", "centrada"]:
        for vecinos in [20, 50, 100, 200]:
            m, _ = evaluar(item_knn(Mv[variante], vecinos), Mv["R"], rel_v, rank_v)
            grid.append({"variante": variante, "vecinos": vecinos, "ndcg@10_validacion": m["ndcg"].mean()})
    grid = pd.DataFrame(grid).round(4)
    mejor = grid.loc[grid["ndcg@10_validacion"].idxmax()]
    variante, vecinos = mejor["variante"], int(mejor["vecinos"])

    # 2) Reentrenar con todo el entrenamiento y evaluar una sola vez en test
    M = matrices(train, iu, ii, forma)
    R, mascara, R_cent, R_pos = M["R"], M["mascara"], M["centrada"], M["positivas"]

    # Rasgos de contenido: mecánicas + temas + dominios (one-hot)
    F = np.zeros((len(items), 0))
    for puente, col in [(jm, "mecanica_id"), (jt, "tema_id")]:
        onehot = pd.crosstab(puente["bgg_id"], puente[col]).reindex(items, fill_value=0)
        F = np.hstack([F, onehot.to_numpy(float)])
    dom = juegos.set_index("bgg_id").loc[items, [c for c in juegos if c.startswith("dom_")]]
    F = np.hstack([F, dom.to_numpy(float)])

    relevantes = relevantes_de(test, iu, ii, len(usuarios))

    pop = R_pos.sum(0)
    pop_rank = pd.Series(-pop).rank(method="min").to_numpy()   # 1 = el más popular

    modelos = {"popularidad (baseline)": popularidad(R_pos),
               "contenido": contenido(R_cent, F),
               "item-kNN": item_knn(M[variante], vecinos)}

    resultados, por_usuario, tops = [], {}, {}
    for nombre, puntos in modelos.items():
        m, top = evaluar(puntos, R, relevantes, pop_rank)
        por_usuario[nombre], tops[nombre] = m, top
        lo, hi = ic_bootstrap(m["ndcg"].to_numpy())
        resultados.append({
            "modelo": nombre, f"precision@{K}": m["precision"].mean(), f"recall@{K}": m["recall"].mean(),
            f"ndcg@{K}": m["ndcg"].mean(), "ndcg_ic95_inf": lo, "ndcg_ic95_sup": hi,
            "cobertura_catalogo": len(np.unique(top)) / len(items),
            "rank_popularidad_medio_recomendado": m["pop_media_rank"].mean(),
        })
    tabla = pd.DataFrame(resultados).round(4)

    # Diferencia pareada item-kNN - baseline (mismos usuarios)
    d = (por_usuario["item-kNN"]["ndcg"].to_numpy() - por_usuario["popularidad (baseline)"]["ndcg"].to_numpy())
    lo, hi = ic_bootstrap(d)

    # Análisis de errores: NDCG por actividad del usuario (nº de valoraciones en entrenamiento)
    n_train = mascara.sum(1)
    grupos = pd.cut(n_train, [0, 15, 40, 10_000], labels=["8-15", "16-40", ">40"])
    errores = []
    for nombre, m in por_usuario.items():
        g = pd.Series(grupos[m["u"]]).astype(str)
        errores.append(m.assign(grupo=g.values).groupby("grupo")["ndcg"].mean().rename(nombre))
    tabla_err = pd.concat(errores, axis=1).round(4)
    tabla_err["usuarios"] = pd.Series(grupos[por_usuario["item-kNN"]["u"]]).astype(str).value_counts()

    # Ejemplo de salida para el frontal: top-10 de item-kNN con su explicación
    nombres = juegos.set_index("bgg_id")["nombre"]
    # Explicación: de los juegos que el usuario puntuó por encima de su media, el más parecido al recomendado
    S = similitud(M[variante])
    ejemplo = []
    u = int(np.argmax(n_train == np.median(n_train))) if (n_train == np.median(n_train)).any() else 0
    puntos_u = np.where(mascara[u], -np.inf, modelos["item-kNN"][u])
    for pos, i in enumerate(tops["item-kNN"][u], 1):
        gustados = np.where(R_cent[u] > 0)[0]
        porque = gustados[np.argmax(S[i, gustados])] if len(gustados) else None
        ejemplo.append({"user_id": int(usuarios[u]), "posicion": pos, "bgg_id": int(items[i]),
                        "juego": nombres[items[i]], "puntuacion": round(float(puntos_u[i]), 3),
                        "porque_te_gusto": nombres[items[porque]] if porque is not None else "",
                        "en_test_y_positivo": i in relevantes[u]})

    SALIDA.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA / "metricas.csv", index=False)
    grid.to_csv(SALIDA / "seleccion_knn_validacion.csv", index=False)
    tabla_err.to_csv(SALIDA / "ndcg_por_actividad.csv")
    pd.DataFrame(ejemplo).to_csv(SALIDA / "ejemplo_recomendaciones.csv", index=False)
    resumen = {
        "item_knn_elegido": {"variante": variante, "vecinos": vecinos},
        "particion": {"train": len(train), "test": len(test), "usuarios_evaluados": int(len(por_usuario["item-kNN"])),
                      "juegos": len(items), "relevantes_test": int(sum(map(len, relevantes)))},
        "diferencia_ndcg_itemknn_menos_baseline": {"media": round(float(d.mean()), 4),
                                                    "ic95": [round(lo, 4), round(hi, 4)]},
    }
    (SALIDA / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))

    pd.set_option("display.width", 160)
    print(grid.to_string(index=False), f"\n-> elegido: {variante}, {vecinos} vecinos\n")
    print(tabla.to_string(index=False))
    print("\nNDCG@10 por actividad del usuario:\n", tabla_err.to_string())
    print("\n", json.dumps(resumen, indent=2, ensure_ascii=False))
    print("\nEjemplo:\n", pd.DataFrame(ejemplo)[["posicion", "juego", "porque_te_gusto", "en_test_y_positivo"]].to_string(index=False))


if __name__ == "__main__":
    main()
