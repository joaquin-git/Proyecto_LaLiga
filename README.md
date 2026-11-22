# Moneyball LaLiga ⚽ — eficiencia salarial de las plantillas

Proyecto de Data Engineering (formación Cívica) con **Snowflake + dbt + Power BI** sobre la liga
española de fútbol masculino, temporadas **2024/25 y 2025/26**.

## 1. El caso de uso

> **"¿Qué jugadores rinden más por cada euro que cobran, cuánto dinero perdemos con los lesionados
> y a quién deberíamos fichar?"**

**Cliente:** la Dirección Deportiva del **Real Betis Balompié**. Es un club de presupuesto medio
(7.º en masa salarial de LaLiga) con el límite de coste de plantilla ajustado: no puede gastar
mucho, así que tiene que gastar bien.

**Por qué es un problema de negocio real:** LaLiga fija a cada club un *límite de coste de plantilla
deportiva*. Cada euro de salario mal invertido (un jugador caro que no juega, o que se pasa media
temporada en la enfermería) es un euro que no se puede usar para fichar. El director deportivo
necesita datos, no intuición, para decidir a quién renovar, vender o fichar.

**Por qué usa los datos de toda la liga:** para comparar a sus jugadores con el precio de mercado
del rendimiento (P1), para comparar su coste de lesiones con el resto de clubes (P2) y porque los
fichajes que recomiendan sus ojeadores están en otros clubes (P3). El modelo sirve igual para
cualquier club: el club se elige con un filtro en Power BI.

**Por qué dos temporadas cerradas:** las decisiones de mercado y de renovaciones se toman con
temporadas completas. Dos y no una, para ver la regularidad de cada jugador (no un año bueno o malo
aislado), su evolución y tener muestra suficiente de lesiones. El pipeline está preparado para seguir
cargando la temporada en curso (modelo incremental y despliegue con jobs).

### Preguntas de negocio

| # | Pregunta | Ejemplo de respuesta (datos del proyecto) |
|---|----------|-------------------------------------------|
| P1 | ¿Cuánto nos cuesta cada minuto jugado, cada gol y cada asistencia de cada jugador? ¿Quién rinde por encima o por debajo de lo que cobra, comparado con la mediana de la liga en su posición? | "Sergi Altimira cuesta ≈ 323 € por minuto, la mitad que un centrocampista medio de LaLiga (≈ 692 €); Isco, ≈ 3.369 €, casi cinco veces más" |
| P2 | ¿Cuánto salario pagamos a jugadores lesionados (coste de enfermería) por tipo de lesión y mes, y cómo estamos frente al resto de clubes? | "El Betis pagó 4,68 M€ a lesionados en dos temporadas (4,4 % de su masa salarial, frente al 5,7 % de la liga); la lesión más cara, la rotura fibrilar de grado I (1,65 M€)" |
| P3 | ¿Qué jugadores de otros clubes recomiendan fichar nuestros ojeadores, y caben en nuestro presupuesto? | "De 1.056 informes, 185 recomiendan fichar: una lista de candidatos con su club y salario actuales, su último traspaso y la posición en la que los ven los ojeadores" |

## 2. Las fuentes de datos

Seis sistemas, cada uno exporta su fichero y escribe los datos a su manera (nombres de club distintos,
fechas en dos formatos, duplicados, homónimos...).

| Sistema | Tabla | Una fila es... | Filas | Responde a |
|---------|-------|----------------|------:|-----------|
| API de LaLiga | `partidos` | un partido | 767 | P1, P3 |
| Proveedor de estadísticas | `estadisticas_jugador_partido` | lo que hizo un jugador en un partido | 22.793 | P1 |
| RRHH | `contratos` | un contrato o renovación (con salario) | 619 | P1, P2, P3 |
| Mercado | `traspasos` | una operación de mercado | 126 | P3 |
| Servicios médicos | `lesiones` | una lesión (con parte médico) | 747 | P2 |
| App de scouting | `informes_scouting` | un informe de un ojeador (texto libre) | 1.056 | P3 |

## 3. Arquitectura (medallion, ELT)

```
FUENTES (6 CSV)      BRONZE                       STAGING            SILVER                      GOLD                         CONSUMO
API partidos    ─┐                                                                                                         
Proveedor stats ─┤   copia fiel, todo VARCHAR     una vista por      modelo entidad-relación     modelo dimensional           Power BI
RRHH contratos  ─┼─► + metadatos de carga    ─►  tabla: renombrar ─► (16 tablas): limpiar,   ─►  (estrella): hechos y     ─►  P1 · P2 · P3
Mercado         ─┤   (COPY INTO, Snowflake)      y castear           deduplicar, unificar         dimensiones por pregunta
Servicio médico ─┤                                                    y normalizar (3FN)                                    
App scouting    ─┘                               └──────────────────────── dbt ──────────────────────────┘
```

- **Bronze:** la ingesta va fuera de dbt (`COPY INTO`). Todo en texto para no rechazar ninguna fila.
- **Staging:** una vista por tabla de bronze; solo renombra y convierte tipos (mismas filas).
- **Silver:** limpia y normaliza. Dato maestro de clubes, países y ligas (seed `alias_clubes`);
  la licencia como clave del jugador (hay homónimos); deduplicado con `qualify`; la tabla de
  estadísticas es **incremental** (`merge`).
- **Gold:** una tabla de hechos por pregunta, con dimensiones de jugador, club y fecha.

**Entornos:** DEV, PRE y PRO, cada uno con sus bases de datos (`{ENV}_LALIGA_{BRONZE|SILVER|GOLD}_DB`)
y su rol, que solo escribe en su entorno. Bronze se carga en DEV y se clona (zero-copy) a PRE y PRO.
A producción solo se llega por merge a `main` y jobs encadenados DEV → PRE → PRO.

## 4. El modelo de gold

| Tabla | Tipo | Una fila es... | Pregunta |
|-------|------|----------------|----------|
| `dim_jugadores` | Dimensión | un jugador | todas |
| `dim_clubes` | Dimensión | un club (con su liga y país) | todas |
| `dim_fechas` | Dimensión | un día (julio 2024 – junio 2026) | P2, P3 |
| `fct_rendimiento_temporada` | Hechos | un jugador en un club en una temporada | **P1** |
| `fct_lesiones` | Hechos | una lesión, con su coste | **P2** |
| `fct_informes_scouting` | Hechos | un informe, con la recomendación del ojeador | **P3** |
| `agg_shortlist_fichajes` | Agregado | un candidato a fichar, con su encaje económico | **P3** |

## 5. Calidad y gobierno

- **Tests:** `unique`, `not_null`, `relationships`, `accepted_values`, `dbt_utils.accepted_range` y
  `dbt_utils.unique_combination_of_columns`; un test singular (los goles de los jugadores cuadran
  con el marcador en los 760 partidos) y un unit test.
- **Macros:** `limpiar_fecha`, `normalizar_nombre` y `generate_schema_name` (esquema por entorno).
- **Documentación** de modelos y columnas, docs block reutilizable y linaje con `dbt docs generate`.
- **Gold:** contratos en las dimensiones, `+grants` de lectura para `LALIGA_REPORTING_ROLE` (Power BI)
  y exposure del informe.

## 6. Cómo ejecutarlo

1. **Snowflake:** ejecutar en orden `snowflake/01_entorno_laliga.sql` (entorno, roles y permisos),
   `02_bronze_laliga.sql` (carga de bronze) y `03_clonar_bronze_laliga.sql` (clones PRE y PRO).
2. **dbt:** variables de entorno `DBT_BRONZE_DB`, `DBT_SILVER_DB` y `DBT_GOLD_DB` con las bases de
   datos de cada entorno; después `dbt deps`, `dbt seed` y `dbt build`.
3. **Despliegue:** jobs `JOB_DEV` → `JOB_PRE` → `JOB_PRO` (target `dev`, `pre`, `pro`).

## 7. Estructura del repositorio

| Carpeta / fichero | Contenido |
|---------|-----------|
| `data/bronze/` | Los 6 CSV de origen (generados) |
| `data/validacion/` | Etiquetas reales de los informes y lesiones, para validar resultados (no se cargan en bronze) |
| `scripts/` | Generador del dataset (`generar_bronze.py`) y datos maestros |
| `snowflake/` | Scripts de entorno (01), carga de bronze (02) y clones PRE/PRO (03) |
| `seeds/` | `alias_clubes`: equivalencias entre los nombres de club de cada fuente y el oficial |
| `models/staging/<sistema>/` | Sources (con freshness y tests) y una vista por tabla de bronze |
| `models/silver/<sistema>/` | Modelo entidad-relación normalizado (16 tablas), con tests y documentación |
| `models/gold/` | Modelo dimensional: dimensiones, hechos y shortlist |
| `macros/` | `limpiar_fecha`, `normalizar_nombre`, `generate_schema_name` |
| `tests/singular/` | Test de negocio: los goles cuadran con el marcador |
| `docs/` | Documentación técnica de cada capa |

## 8. Estado

| Fase | Estado |
|------|--------|
| Caso de uso y dataset | ✅ |
| Snowflake: entorno, carga de bronze y clones PRE/PRO | ✅ |
| dbt: conexión, variables de entorno, sources, seeds y staging | ✅ |
| Silver (modelo entidad-relación, 16 tablas, una incremental) | ✅ |
| Calidad: 119 tests, documentación y macros | ✅ |
| Despliegue DEV → PRE → PRO con jobs | ✅ |
| Gold (modelo dimensional, 7 tablas) | ✅ |
| Power BI | ⬜ |

**Documentación técnica:**
- Configuración de Snowflake y dbt: [`docs/00_configuracion_dbt_snowflake.md`](docs/00_configuracion_dbt_snowflake.md)
- Capa bronze: [`docs/01_bronze.md`](docs/01_bronze.md)
- Seed y capa staging: [`docs/02_staging.md`](docs/02_staging.md)
- Capa silver: [`docs/03_silver.md`](docs/03_silver.md)
- Calidad, documentación y macros: [`docs/04_calidad_y_macros.md`](docs/04_calidad_y_macros.md)
- Capa gold (modelo dimensional): [`docs/05_gold.md`](docs/05_gold.md)

## 9. Limitaciones y mejoras futuras

- **Datos simulados** donde no son públicos (ver aviso). Con los datos reales del club, el modelo es el mismo.
- **La recomendación del ojeador** se extrae del texto con una regla de negocio (los ojeadores cierran
  con frases estándar). Si escribieran libremente, se clasificaría con un modelo de lenguaje
  (por ejemplo, Snowflake Cortex), no disponible en la cuenta de prueba.
- **Foto de contratos de julio de 2026:** los movimientos posteriores llegarían con nuevas cargas.

## ⚠️ Aviso sobre los datos

Clubes, estadios, árbitros y nombres de jugadores son **reales**, y las plantillas y traspasos se
aproximan a lo que pasó en esas temporadas (pueden tener imprecisiones).
**Todo lo demás es SIMULADO con fines didácticos:** salarios, cláusulas, estadísticas de partido,
resultados, lesiones (salvo tres lesiones largas que fueron públicas), partes médicos, informes de
scouting, fechas de nacimiento exactas, agentes, agencias, médicos y ojeadores. No representan
información real de ninguna persona. Se recomienda mantener el repositorio **privado**.
