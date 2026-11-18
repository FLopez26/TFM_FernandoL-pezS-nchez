# Entrega 04 · Diseño del frontal y experiencia de usuario

**Proyecto:** recomendador de juegos de mesa 

El mockup es un HTML funcional y sencillo (`frontend/index.html`) que usa el modelo de la entrega 3.

```bash
python src/exportar_modelo_web.py   # genera frontend/datos_modelo.js a partir del Gold
# después, abrir frontend/index.html
```

## 1. Utilidad y valor

- **A quién va dirigido:** aficionados a los juegos de mesa que quieren saber qué juego probar o comprar después, sin revisar foros ni rankings.
- **Funcionalidades del MVP:**
  1. Indicar los juegos que ya se tienen.
  2. Recibir 10 recomendaciones, cada una explicada.
  3. Filtrar por número de jugadores, duración y complejidad.
- **Qué permite decidir:** qué juego comprar, regalar o jugar a continuación, con un motivo y los datos prácticos de cada juego para comprobar si encaja con su grupo.

## 2. Flujo de usuario

1. Entra y ve directamente los juegos más populares. Así no hay una pantalla vacía.
2. Añade sus juegos con un buscador que sugiere nombres mientras escribe.
3. Recibe el top-10, que se actualiza al momento con cada juego que añade o quita.
4. Afina con filtros opcionales: cuántos juegan, duración máxima y complejidad.
5. Actúa sobre cada recomendación: "Ya lo tengo" lo añade a su colección y recalcula, "No me interesa" lo descarta y "Ver en BGG" abre la ficha completa.

## 3. Diseño del frontal

**Pantalla principal**, con una colección de 5 juegos:

![Pantalla principal](img/mockup_principal.png)

| Estado inicial: sin juegos, se muestra lo popular | Con filtros: 2 jugadores, máximo 1 hora |
|---|---|
| ![Inicio](img/mockup_inicio.png) | ![Filtros](img/mockup_filtros.png) |

## 4. Experiencia de usuario

- **Dos columnas y tres pasos numerados.** A la izquierda lo que introduce el usuario y a la derecha lo que recibe. El orden de lectura coincide con el del flujo.
- **Una lista en vez de gráficos.** El resultado es un ranking, y una lista numerada es lo más rápido de leer. Cada tarjeta muestra solo lo que sirve para decidir: jugadores, duración, complejidad y ranking en BGG.
- **Explicación en cada recomendación.** "Porque tienes X" es el juego de la colección del usuario más parecido al recomendado según el modelo. Da confianza y permite descartar rápido.
- **Puntuación sin cifras engañosas.** La puntuación del modelo no es una nota ni una probabilidad, así que no se muestra como número. Se representa con una barra de **afinidad relativa** respecto a la primera recomendación (alta, media o baja).
- **Resultados inciertos y errores.** Un mensaje de estado arriba cambia según la situación:
  - **Sin juegos:** se avisa de que se muestran los populares.
  - **Con 1 o 2 juegos:** se avisa de que la recomendación todavía es poco fiable. En la entrega 3 el modelo apenas superaba a la popularidad con usuarios de pocas valoraciones.
  - **Con 3 o más juegos:** se confirma que la recomendación es personal.
  - **Si los filtros no dejan resultados:** se pide quitar alguno.
  - **Si un juego no está en el catálogo de la demo:** el buscador lo dice.
- **Controles mínimos:** un buscador, tres desplegables y dos botones por tarjeta. Sin registro.

## 5. Continuidad hacia el MVP final

`src/exportar_modelo_web.py` entrena el modelo elegido en la entrega 3 (item-kNN binario) con el Gold de la entrega 2. Después guarda en `frontend/datos_modelo.js` los 200 vecinos de cada juego con su similitud, junto con la ficha de `juegos.csv`. El navegador hace el mismo cálculo que el modelo: suma las similitudes con los juegos del usuario. Se ha comprobado que, para la misma colección, el top-10 de la web coincide con el de Python. Los filtros usan las columnas `min_jugadores`, `max_jugadores`, `duracion_min` y `peso` del Gold.

