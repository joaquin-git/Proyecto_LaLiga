# Paso 2 · Capa BRONZE

## 1. Qué es bronze y qué decisiones hemos tomado

Bronze (o RAW) es la **copia fiel de lo que llega de las fuentes**. Aquí no se limpia ni se
normaliza nada: si el origen trae "Barça" y "FC Barcelona", bronze guarda las dos cosas. Así
siempre podemos volver a reconstruir silver y gold desde el dato original (trazabilidad y linaje).

| Decisión | Justificación |
|----------|---------------|
| **6 tablas, una por fuente** | Cada sistema operacional exporta su propio fichero. Bronze respeta esa separación: no mezcla fuentes. |
| **Tablas desnormalizadas** | Así llegan los datos de los sistemas: cada fichero repite información (el estadio en cada partido, los datos del jugador en cada estadística, la agencia en cada contrato...). Normalizar es trabajo de silver. |
| **Todas las columnas `VARCHAR`** | Si una fila trae `"6,8"` en una columna numérica, una tabla tipada haría fallar la carga. En bronze **no se puede perder ni rechazar ningún dato**; el tipado y la limpieza se hacen en silver. |
| **Columnas de auditoría** `_FECHA_EXTRACCION`, `_FICHERO_ORIGEN`, `_FECHA_CARGA` | Gobierno del dato: saber de qué fichero viene cada fila y cuándo se cargó. Sirven para deduplicar y para la carga delta. |
| **Carga con `COPY INTO` desde un stage interno** (ELT) | La ingesta va **fuera de dbt**: se copia el dato en bruto a Snowflake y dbt transforma dentro del almacén (bronze → silver → gold). Los *seeds* de dbt están pensados para tablas pequeñas y estáticas (catálogos), no para cargar datos de origen. |
| **Carga completa (full)** | Son ficheros históricos de dos temporadas. En un caso real, las estadísticas usarían **carga delta** por `_FECHA_EXTRACCION`. |

## 2. Las 6 tablas

| Tabla | Fuente simulada | Una fila es... | Filas aprox. |
|-------|-----------------|----------------|-------------:|
| `RAW_PARTIDOS` | API de LaLiga (calendario y resultados) | un partido | 767 |
| `RAW_ESTADISTICAS_JUGADOR_PARTIDO` | Proveedor externo de estadísticas | un jugador que jugó en un partido | 22.800 |
| `RAW_CONTRATOS` | Departamento de RRHH / registro de contratos | un contrato (o renovación) de un jugador con un club | 620 |
| `RAW_TRASPASOS` | Departamento de mercado | una operación de mercado (traspaso, cesión, libre, fin de cesión) | 126 |
| `RAW_LESIONES` | Servicios médicos de los clubes | una lesión de un jugador | 750 |
| `RAW_INFORMES_SCOUTING` | App de scouting (texto libre) | un informe de un ojeador sobre un jugador en un partido | 1.050 |

Volumen: 2 temporadas × 380 partidos, 23 clubes (20 por temporada: 3 descienden y 3 ascienden),
unos 470 jugadores.

### 2.1 RAW_PARTIDOS
`ID_PARTIDO, TEMPORADA, JORNADA, FECHA_PARTIDO, HORA, EQUIPO_LOCAL, EQUIPO_VISITANTE, ESTADIO,
CIUDAD_ESTADIO, AFORO_ESTADIO, GOLES_LOCAL, GOLES_VISITANTE, RESULTADO, ESPECTADORES, ARBITRO`

### 2.2 RAW_ESTADISTICAS_JUGADOR_PARTIDO
`ID_PARTIDO, TEMPORADA, FECHA_PARTIDO, ID_JUGADOR_PROVEEDOR, JUGADOR, FECHA_NACIMIENTO,
NACIONALIDAD, EQUIPO, RIVAL, CONDICION, POSICION, TITULAR, MINUTOS, GOLES, ASISTENCIAS, TIROS,
TIROS_A_PUERTA, PASES_INTENTADOS, PASES_COMPLETADOS, RECUPERACIONES, TARJETAS_AMARILLAS,
TARJETAS_ROJAS, VALORACION`

### 2.3 RAW_CONTRATOS
`ID_CONTRATO, CODIGO_LICENCIA, JUGADOR, FECHA_NACIMIENTO, NACIONALIDADES, POSICION, EQUIPO,
CIUDAD_EQUIPO, TIPO_CONTRATO, CLUB_PROPIETARIO, FECHA_INICIO, FECHA_FIN_PREVISTA, FECHA_BAJA,
ESTADO_CONTRATO, SALARIO_BRUTO_ANUAL_EUR, CLAUSULA_RESCISION_EUR, AGENTE, AGENCIA_REPRESENTACION,
EMAIL_AGENCIA`

- `ESTADO_CONTRATO`: Vigente · Renovado (sustituido por otro contrato nuevo) · Finalizado ·
  Rescindido por traspaso · Cedido a otro club · Cesión finalizada.
- Una **renovación genera una fila nueva** con otro salario: es la base del histórico (SCD tipo 2) en gold.

### 2.4 RAW_TRASPASOS
`ID_OPERACION, FECHA_OPERACION, VENTANA, JUGADOR, NACIONALIDAD, POSICION, CLUB_ORIGEN, LIGA_ORIGEN,
PAIS_ORIGEN, CLUB_DESTINO, LIGA_DESTINO, PAIS_DESTINO, TIPO_OPERACION, IMPORTE`

### 2.5 RAW_LESIONES
`ID_LESION, CODIGO_LICENCIA, JUGADOR, EQUIPO, TEMPORADA, FECHA_LESION, FECHA_ALTA, TIPO_LESION,
ZONA_CORPORAL, DIAS_BAJA, PARTIDOS_PERDIDOS, MEDICO_RESPONSABLE, PARTE_MEDICO`

- `PARTE_MEDICO` es **texto libre** → en gold lo leerá `AI_FILTER` ("¿es una lesión recurrente?",
  "¿es grave?").

### 2.6 RAW_INFORMES_SCOUTING
`ID_INFORME, FECHA_INFORME, OJEADOR, EMAIL_OJEADOR, ZONA_OJEADOR, JUGADOR, EQUIPO_JUGADOR,
PARTIDO_OBSERVADO, FECHA_PARTIDO, POSICIONES_OBSERVADAS, NOTA_GLOBAL, INFORME`

- `INFORME` es **texto libre**, escrito por seis ojeadores con estilos distintos (unos redactan
  párrafos y otros escriben telegramas como "Dudas. Seguir.") → en gold lo leerán `AI_CLASSIFY`
  (Fichar / Seguir observando / Descartar) y `AI_COMPLETE` (resumen para el director deportivo).
- En `data/validacion/` está la recomendación "real" de cada informe, para **medir la precisión de
  la IA**: así podrás decir "Cortex acierta el X %".

## 3. Problemas de calidad que traen los datos (a propósito)

Esto es lo que justificará cada transformación de silver. Cada problema tiene su regla:

| # | Problema | Dónde | Qué haremos en silver |
|---|----------|-------|-----------------------|
| 1 | **Un mismo club con varios nombres** ("Barça", "FC Barcelona", "Barcelona"; "Atleti", "At. Madrid"...) | todas | Tabla maestra de clubes + mapeo de alias → una sola clave |
| 2 | **Fechas en varios formatos** (`2024-08-16`, `16/08/2024`) | partidos, estadísticas, contratos, lesiones, traspasos | `TRY_TO_DATE` con varios formatos → `DATE` |
| 3 | **Filas duplicadas** (re-extracciones) | partidos (7), estadísticas (≈160) | `QUALIFY ROW_NUMBER() OVER (PARTITION BY clave ORDER BY _FECHA_EXTRACCION DESC) = 1` |
| 4 | **Números como texto con formato** (`"4.500.000 €"`, `"42M"`, `"25,5M"`, `"Libre"`, `"N/D"`) | contratos (salario), traspasos (importe), partidos (aforo) | Limpieza a `NUMBER`; "Libre"/"Cesión" → 0, "N/D" → NULL |
| 5 | **Decimales con coma** (`"6,8"`) | estadísticas (valoración), scouting (nota) | `REPLACE(',', '.')` + `TRY_TO_DECIMAL` |
| 6 | **Booleanos inconsistentes** (`S/N`, `true/false`) | estadísticas (titular) | → `BOOLEAN` |
| 7 | **Nombres de jugador sucios** (MAYÚSCULAS, espacios, sin tildes: "Jesus Areso") | estadísticas, lesiones, scouting | `TRIM`, `INITCAP` y comparar sin tildes (`TRANSLATE`/`COLLATE`) |
| 8 | **Homónimos**: dos jugadores reales llamados "Juan Cruz" (Osasuna y Leganés) | todas | **Nunca usar el nombre como clave**: licencia o nombre + fecha de nacimiento |
| 9 | **Celdas con listas** (1FN): `NACIONALIDADES = "Marruecos; España"`, `POSICIONES_OBSERVADAS = "Pivote, Interior"` | contratos, scouting | Tablas puente (N:M) con `SPLIT_TO_TABLE` / `LATERAL FLATTEN` |
| 10 | **Cada fuente identifica al jugador a su manera**: el proveedor con `ID_JUGADOR_PROVEEDOR`, RRHH y médicos con `CODIGO_LICENCIA`, scouting solo con el nombre | todas | Tabla maestra de jugadores con la licencia como clave de negocio + mapeo de IDs |
| 11 | **Dependencias transitivas** (3FN): agencia → email de agencia; estadio → ciudad y aforo; club → ciudad | contratos, partidos | Tablas propias: `AGENCIA`, `ESTADIO`, `CLUB` |
| 12 | **Temporada escrita de dos formas** (`2024/25` y `2024-2025`) | partidos | Normalizar a `2024/25` y tabla `TEMPORADA` |
| 13 | **Campos vacíos** (espectadores, fecha de alta, valoración, cláusula) | varias | Decidir caso a caso: NULL justificado o derivado (fecha_alta = fecha_lesion + dias_baja) |
| 14 | **Clubes que no son de LaLiga** (Liverpool, Al-Nassr...) solo en traspasos | traspasos | ¿Van a la tabla `CLUB` con su liga? → decisión de modelado (la veremos en silver) |
| 15 | **El estadio no es fijo del club**: el Barça juega en Montjuïc (24/25), Johan Cruyff y Spotify Camp Nou (25/26) | partidos | El estadio es atributo del **partido**, no del club |

## 4. Cómo cargarlo en Snowflake

1. Ejecuta `snowflake/00_usuario_dbt.sql` (rol y usuario para dbt). Solo la primera vez.
2. Ejecuta la primera parte de `snowflake/01_bronze_ddl_y_carga.sql`, hasta el `CREATE STAGE`.
3. Sube los 6 CSV de `data/bronze/` al stage:
   **Snowsight → Data → Databases → LALIGA_DB → BRONZE → Stages → STG_RAW → "+ Files"**.
4. Ejecuta el resto del script: crea las 6 tablas y hace los `COPY INTO`.
5. La última consulta muestra el recuento de filas de cada tabla. Debe coincidir con la tabla del
   apartado 2.

> El script se **genera automáticamente** desde `scripts/generar_bronze.py`, así que las columnas
> del SQL siempre coinciden con las de los CSV.
