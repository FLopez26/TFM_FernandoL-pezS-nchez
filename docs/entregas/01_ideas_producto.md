## Idea 1 — Recomendador de juegos de mesa (sistemas de recomendación)

Motor de recomendación que, a partir de las valoraciones y características de decenas de miles de
juegos de mesa, sugiere a cada usuario qué juego jugar o comprar a continuación.

### Problema que resuelve

* **Qué ocurre actualmente.** El catálogo de juegos de mesa es enorme y crece cada año. Para un
aficionado es muy difícil descubrir títulos que realmente le van a gustar; para una tienda
especializada o para alguien que busca un regalo, acertar es complicado.
* **Por qué supone un problema.** Es un problema clásico de sobrecarga de opciones y de "cola larga":
muchos juegos buenos quedan invisibles, y los nuevos usuarios no tienen historial en el que basar
una recomendación.
* **Qué decisión o proceso podría mejorar con datos.** La decisión de qué juego comprar o jugar, qué
recomendar a un cliente o qué stock priorizar en una tienda.
* **Por qué no es solo un ejercicio técnico.** Es un problema de descubrimiento real, con una comunidad
y un componente comercial claros detrás.

### Motivación para realizar el proyecto

* **Interés técnico.** Los sistemas de recomendación son un tema que están a la orden del día y me gustaría profundizar en ellos.
* **Motivación personal.** Los juegos de mesa me resultan cercanos, lo que ayuda a sostener el
proyecto y el reto técnico sigue siendo plenamente serio ya que pretendo que funcione para todo aquel que lo necesite.
* **Utilidad para un colectivo concreto.** Aficionados, tiendas especializadas y editoriales.
* **Viabilidad de datos.** Existen datasets públicos de BoardGameGeek en Kaggle pensados explícitamente
para sistemas de recomendación. Además, la propia API XML de BGG permite obtener
datos y metadatos de cada juego.

### A quién impacta

* Aficionados a los juegos de mesa que quieren descubrir títulos afines a sus gustos.
* Tiendas especializadas, que pueden recomendar mejor y ajustar su catálogo.
* Editoriales y diseñadores, interesados en entender qué características gustan a cada perfil.
* Personas que buscan un regalo y no conocen el sector.

### Por qué tiene valor

* **Mejor experiencia de usuario** y descubrimiento de la "cola larga".
* **Ahorro de tiempo** en la búsqueda y elección.
* **Apoyo a decisiones de negocio** para tiendas y editoriales.
* **Generación de conocimiento** sobre qué mecánicas, temas o características impulsan las preferencias.



## Idea 2 — Geografía electoral de España: qué explica el voto por municipios

Análisis que cruza los resultados electorales oficiales con datos socioeconómicos y territoriales a
nivel de municipio para entender, segmentar y visualizar los patrones de voto en España.

### Problema que resuelve

* **Qué ocurre actualmente.** Existen resultados electorales oficiales muy detallados (por municipio,
incluso por mesa) de todas las convocatorias, y una gran cantidad de datos socioeconómicos del INE
(renta, edad, paro, densidad, nivel educativo, envejecimiento…), pero cada fuente va por su lado. El
"porqué" del voto se comenta en tertulias, rara vez con un análisis sistemático y reproducible que
cruce ambas cosas a nivel local.
* **Por qué supone un problema.** Sin relacionar resultados con contexto socioeconómico y territorial,
es difícil entender patrones (urbano/rural, costa/interior, "España vaciada"), segmentar territorios
o comparar convocatorias de forma rigurosa.
* **Qué decisión o proceso podría mejorar con datos.** El análisis político y periodístico, la
planificación territorial de organizaciones y campañas, y la comprensión del comportamiento electoral.
* **Por qué no es solo un ejercicio técnico.** Entender el voto y su relación con el territorio es un
caso de uso real para medios, investigación y actores políticos.

### Motivación para realizar el proyecto

* **Relevancia social y política**, como ya he comentado es muy complicado encontrar algo del ámbito de la política neutral que analice los datos para poder entender que ocurre realmente en cada municipio.
* **Interés técnico.** Combina EDA y estadística (correlaciones, regresión), *clustering* de municipios
para descubrir perfiles de voto y una fuerte componente geoespacial (mapas coropléticos).
* **Utilidad para un colectivo concreto.** Medios, investigadores y organizaciones que analizan el
territorio.
* **Viabilidad de datos.** El Ministerio del Interior publica en Infoelectoral los resultados por
municipio de todas las elecciones y referéndums desde 1976, en ficheros descargables. Las tablas de
municipios se decodifican con las del INE, de donde se obtienen además las variables socioeconómicas,
y existen *shapefiles* oficiales para los mapas.

### A quién impacta

* Periodistas y analistas políticos, que necesitan explicar y contextualizar resultados.
* Investigadores en ciencia política y sociología.
* Organizaciones y campañas que planifican su estrategia por territorio.
* Ciudadanía interesada en entender el comportamiento electoral de su zona.

### Por qué tiene valor

* **Generación de conocimiento** sobre el comportamiento electoral y su relación con el territorio.
* **Mejor segmentación** territorial (perfiles de municipios).
* **Apoyo a la toma de decisiones** de medios, investigación y campañas.
* **Mayor transparencia** mediante visualizaciones claras y reproducibles.



## Idea 3 — Motor de inteligencia de clientes: segmentación, valor de vida (CLV) y riesgo de fuga

Producto de datos que, a partir del histórico de transacciones de una empresa, segmenta su base de
clientes, predice el valor futuro de cada cliente (Customer Lifetime Value) y su riesgo de fuga, para
priorizar el gasto en marketing y en retención. Está pensado como una solución horizontal, aplicable a
cualquier empresa con clientes recurrentes.

### Problema que resuelve

* **Qué ocurre actualmente.** La mayoría de pymes y comercios acumulan un histórico de ventas o
transacciones que apenas explotan. Tratan a todos los clientes por igual, invierten en captación sin
saber a quién conviene retener y no distinguen al cliente de alto valor del ocasional.
* **Por qué supone un problema.** Se malgasta presupuesto de marketing, se pierden clientes valiosos por
no actuar a tiempo y las decisiones se toman por intuición, cuando captar un cliente nuevo suele
costar bastante más que retener uno existente.
* **Qué decisión o proceso podría mejorar con datos.** A quién dirigir cada campaña, en qué clientes
invertir esfuerzos de retención y con qué prioridad, y cómo repartir el presupuesto comercial.
* **Por qué no es solo un ejercicio técnico.** Es una decisión de negocio con retorno económico directo,
no un modelo sin destinatario.

### Motivación para realizar el proyecto

* **Relevancia empresarial y económica.** El retorno es tangible: mejor ROI (Retorno de la Inversión) de marketing y mayor
retención de clientes valiosos.
* **Escalabilidad y potencial comercial.** Es un producto replicable: cualquier empresa con clientes
recurrentes (e-commerce, suscripción, servicios, retail) lo necesita, y puede ofrecerse como servicio
conectándolo al histórico de cada cliente.
* **Interés técnico.** Combina RFM, *clustering* para la segmentación, modelos de CLV (regresión o
modelos probabilísticos), predicción de fuga (clasificación) con explicabilidad de por qué cada cliente
está en riesgo, y un cuadro de mando en Power BI.
* **Viabilidad de datos.** Para construir y demostrar el producto existe el dataset Online Retail II de
la UCI: transacciones reales de dos años de un comercio online (cliente, producto, cantidad, precio,
país), con más de un millón de registros, descargable libremente. En un despliegue real, el sistema se
alimentaría del histórico de transacciones del propio cliente.

### A quién impacta

* Pymes y comercios con histórico de ventas pero sin equipo de datos propio.
* Equipos de marketing y CRM que deciden dónde invertir.
* Negocios de e-commerce, suscripción y servicios con clientes recurrentes.
* Consultoras que quieran ofrecer analítica de clientes como servicio.

### Por qué tiene valor

* **Ahorro y optimización** del gasto de marketing (mejor ROI).
* **Detección temprana** de clientes valiosos en riesgo de fuga.
* **Mejor toma de decisiones** y priorización de esfuerzos comerciales.
* **Automatización y escalabilidad**: una misma solución replicable a muchas empresas.



## Idea 4 (adicional) — Analizador de draft de League of Legends esports

Como pequeña presentación antes de explicar de que trata League of Legends. Es un videojuego con una gran escena competitiva (Esports) creada durante años el cual es un 5v5 donde hay que derribar la base rival con una gran cantidad de variables durante la partida. Unas de esas variables son los personajes que se seleccionan y porque, en eso me gustaría centrarme.

Entiendo que pueda ser muy nicho, pero si que me gustaría dejar la idea plasmada porque, como explico a continuación, veo una utilidad y un uso/rentabilidad posible.



Herramienta que, a partir del histórico de partidas profesionales de LoL, analiza la fase de draft
(picks y bans): mide la ventaja de composición, cuantifica sinergias y *counters*, y explora la
predicción del resultado y del siguiente pick a partir del draft. Se plantea como idea de menor
viabilidad para un TFM cerrado, pero de fuerte interés personal.

### Problema que resuelve

* **Qué ocurre actualmente.** En LoL competitivo, la fase de draft decide buena parte de la partida
antes de que empiece, pero su análisis se hace de forma cualitativa (casters, analistas) o con
herramientas propietarias internas de los equipos. No existe una herramienta pública, reproducible
y basada en datos que evalúe la calidad de un draft o sugiera picks/bans.
* **Por qué supone un problema.** Sin datos, las decisiones de draft dependen de la intuición; es difícil cuantificar sinergias y *counters*, medir la ventaja de una composición o comparar tendencias entre ligas y parches.
* **Qué decisión o proceso podría mejorar con datos.** La preparación de draft de equipos,
el trabajo de analistas y creadores de contenido, y el aprendizaje de jugadores.
* **Por qué no es solo un ejercicio técnico.** El draft es una decisión estratégica real con impacto
directo en el resultado; los equipos profesionales dedican recursos específicos a prepararlo.

### Motivación para realizar el proyecto

* **Motivación personal.** Es el dominio que más me interesa (esports de LoL) y sobre el que ya tengo
familiaridad previa trabajando con la API de Leaguepedia (fuente de datos con toda la información del LoL competitivo), lo que hace el proyecto especialmente motivador.
* **Interés técnico.** Combina análisis de secuencias (orden de picks y bans), modelado de *win rate*
condicionado a la composición, métricas de sinergia y *counter*, predicción del resultado a partir
del draft (clasificación) y, en su versión más ambiciosa, recomendación del siguiente pick/ban.
* **Utilidad para un colectivo concreto.** Equipos, *coaches*, analistas, medios y comunidad competitiva.
* **Por qué es menos viable.** Hay miles de opciones posibles en cada partida y dependiendo de en que época se juegue puede depender una selección u otra. Tener todas estas variables pensadas es un gran trabajo y llevaría tiempo.
* **Viabilidad de datos.** Oracle's Elixir publica ficheros CSV descargables y gratuitos con las
partidas profesionales de las grandes ligas desde 2014, un fichero por año, incluyendo los picks y bans de cada partida. La API de Leaguepedia (lol.fandom.com, MediaWiki/Cargo) permite enriquecer con parche, torneo, jugadores y tablas de picks/bans, y la API oficial de Riot (empresa desarrolladora) da acceso a partidas.

### A quién impacta

* Equipos, *coaches* y analistas de esports de LoL.
* Creadores de contenido y medios especializados.
* Jugadores de alto nivel y comunidad competitiva.
* Casas de análisis y predicción de resultados.

### Por qué tiene valor

* **Apoyo a decisiones de draft** con datos en lugar de solo intuición.
* **Generación de conocimiento** sobre sinergias, *counters* y tendencias de meta.
* **Mejor contenido analítico y educativo** para medios y comunidad.

