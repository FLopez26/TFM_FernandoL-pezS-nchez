# Entrega 03 · Machine Learning

**Proyecto:** recomendador de juegos de mesa

Usa el Gold de la entrega 2 (`data/gold/`), con 500 juegos y 920 usuarios. Todo se reproduce con:

```bash
python src/ml_recomendador.py      # < 2 s; resultados en results/entrega03/
```

## 1. Qué problema resuelve

El producto debe proponer a cada aficionado qué juego probar o comprar a continuación, a partir de los que ya ha valorado. Es un problema de recomendación: para cada usuario, se ordenan los juegos que no ha valorado y se le muestran los 10 primeros. Lo usa el aficionado para elegir su próximo juego y, más adelante, una tienda para sugerir productos ("si te gustó X…").

## 2. Datos de entrada y salida

- **Entrada:** las valoraciones del usuario (`valoraciones`: `user_id`, `bgg_id`, `nota`) y, en el modelo por contenido, las mecánicas, los temas y los dominios de cada juego (`juego_mecanica`, `juego_tema`, `juegos`).
- **Salida:** una lista de 10 juegos por usuario, cada uno con una puntuación de orden.
- **Objetivo para evaluar:** acertar los juegos que el usuario valoró con nota ≥ 7 y que se apartaron del entrenamiento.
- **Disponible en el momento de uso:** las notas que el usuario ya ha dado y el catálogo. No se usa nada que dependa de las valoraciones futuras.
- **Riesgos que se controlan:**
  - **Fuga de información:** `nota_bayes_bgg` y `n_valoraciones_bgg` del Gold se calculan con todas las notas de BGG, incluidas las de test. Por eso no se usan: la popularidad se cuenta solo con el entrenamiento.
  - **Sesgo:** el 76 % de las notas son ≥ 7, y el catálogo demo son los 500 juegos más populares. Esto favorece a la popularidad.

## 3. Baseline y modelos

| Modelo | Idea | Por qué |
|---|---|---|
| **Popularidad** (baseline) | Los juegos con más notas positivas en entrenamiento, iguales para todos | Referencia mínima que cualquier modelo debe superar |
| **Por contenido** | Perfil del usuario = sus juegos en mecánicas, temas y dominios, ponderados por nota; se recomiendan los más parecidos (coseno) | Sirve para juegos sin valoraciones y es fácil de explicar |
| **Item-kNN** (colaborativo) | Dos juegos se parecen si los valoran los mismos usuarios; se recomiendan los más parecidos a los del usuario | Modelo colaborativo clásico, sencillo e interpretable |

En el item-kNN, la variante (matriz binaria de "ha valorado" o notas centradas) y el número de vecinos (20, 50, 100 o 200) **se eligieron en un conjunto de validación**, no en test. Ganó la binaria con 200 vecinos: NDCG@10 de 0,160 en validación, frente a 0,055-0,058 de las notas centradas.

## 4. Validación y evaluación

**Partición.** Las valoraciones no tienen fecha, así que no cabe una partición temporal. Para cada usuario se reserva al azar el 20 % de sus valoraciones como test (8.689 valoraciones; semilla 42). Dentro del 80 % restante se separa otro 20 % como validación para elegir la variante. El test solo se usa una vez. Se evalúa a 914 usuarios con al menos un juego positivo en test.

**Métricas** (top-10 sobre los juegos no valorados en entrenamiento):
- **precision@10:** proporción de los 10 recomendados que son positivos en test.
- **recall@10:** proporción de los positivos de test que aparecen en el top-10.
- **NDCG@10:** como el recall, pero premia que los aciertos estén arriba.
- **Cobertura:** proporción del catálogo que llega a recomendarse a algún usuario.

| Modelo | precision@10 | recall@10 | NDCG@10 (IC 95 %) | Cobertura | Rank de popularidad medio de lo recomendado |
|---|---|---|---|---|---|
| Popularidad (baseline) | 0,102 | 0,160 | 0,159 (0,147-0,172) | 9,8 % | 9 |
| Por contenido | 0,039 | 0,050 | 0,056 (0,048-0,064) | 96,6 % | 235 |
| **Item-kNN** | **0,137** | **0,211** | **0,211 (0,197-0,225)** | **58,6 %** | **54** |

El item-kNN mejora el NDCG@10 del baseline en **+0,052** (IC 95 % por bootstrap pareado: 0,040-0,064, un +33 %). Además, recomienda casi seis veces más catálogo. El modelo por contenido queda por debajo del baseline: las mecánicas y los temas, por sí solos, no bastan para predecir qué valorará alguien.

**Errores y limitaciones** (NDCG@10 por actividad del usuario, `results/entrega03/ndcg_por_actividad.csv`):

| Valoraciones del usuario en entrenamiento | Usuarios | Popularidad | Item-kNN |
|---|---|---|---|
| 8-15 | 269 | 0,126 | 0,144 |
| 16-40 | 358 | 0,131 | 0,184 |
| > 40 | 287 | 0,226 | 0,308 |

- Con pocas valoraciones, el item-kNN apenas mejora a la popularidad. Para usuarios nuevos hará falta otro enfoque (popularidad o un cuestionario inicial).
- La variante binaria aprende "qué juegos valora gente como tú", no si te gustarán. Puede recomendar un juego que el usuario conocerá pero puntuará bajo.
- Sigue habiendo sesgo hacia lo popular: el rank medio de lo recomendado es 54 de 500.
- El resultado depende de una única partición aleatoria sobre una muestra de 920 usuarios. Las cifras son orientativas.

## 5. Decisión y uso en el producto

Se elige el **item-kNN binario** como modelo de la demo. Supera al baseline con un margen cuyo intervalo de confianza no incluye el 0, es rápido y cada recomendación se puede explicar. Para el MVP basta como primera versión, con dos condiciones:
- usar popularidad cuando el usuario tenga menos de unas 10 valoraciones;
- entrenarlo sobre el catálogo completo antes de valorar la cola larga.

**Salida para el frontal** (ejemplo en `results/entrega03/ejemplo_recomendaciones.csv`):

| Campo | Significado |
|---|---|
| `posicion` | 1-10, orden de la recomendación |
| `bgg_id`, `juego` | Juego recomendado (no valorado aún por el usuario) |
| `puntuacion` | Puntuación relativa del modelo. Solo sirve para ordenar: no es una nota ni una probabilidad |
| `porque_te_gusto` | El juego que el usuario puntuó por encima de su media y que más se parece al recomendado. Sirve para la explicación "porque te gustó X" |