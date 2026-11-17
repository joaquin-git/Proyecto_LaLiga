# Paso 5 · Calidad, documentación y macros

## 1. Tests

| Dónde | Tests | Qué comprueban |
|-------|------:|----------------|
| Sources (bronze) | 11 | Identificadores no nulos; únicos donde la fuente lo garantiza |
| Seed `alias_clubes` | 3 | Alias único y no nulo |
| Silver: tests genéricos | 117 | Ver tabla siguiente |
| Silver: test singular | 1 | Los goles de los jugadores cuadran con el marcador |
| Silver: unit test | 1 | La lógica de normalización de temporadas |

Resultado: `dbt test --select silver` → **119 PASS**.

### Tests genéricos en silver

| Test | Dónde |
|------|-------|
| `unique` + `not_null` | Todas las claves primarias |
| `relationships` | Todas las claves foráneas |
| `accepted_values` | Posición, tipo y estado de contrato, tipo de operación, temporada |
| `dbt_utils.accepted_range` | Notas 0-10, minutos 0-120, goles, importes, aforo y espectadores ≥ 0, salario > 0 |
| `dbt_utils.unique_combination_of_columns` | Claves compuestas: actuaciones, nacionalidades, posiciones de informe |

Criterios:
- `nombre_jugador` es `not_null` pero no `unique` (homónimos).
- `espectadores` no es `not_null`: falta en 21 partidos de origen.
- `relationships` y `unique` ignoran los nulos: `club_propietario_id` (solo en cesiones) y
  `jugador_proveedor_id` no llevan `not_null`.

### Test singular: `tests/singular/assert_goles_cuadran_con_marcador.sql`

Compara, para cada partido y equipo, la suma de goles de sus jugadores con el marcador. Cruza dos
sistemas distintos (API de partidos y proveedor de estadísticas).

`severity='error', warn_if='>0', error_if='>10'`: hasta 10 descuadres es un aviso (pueden ser goles en
propia puerta, que no son de ningún jugador del equipo); más de 10, error.

### Unit test: `test_temporadas_unifica_formato`

En `_api_laliga__models.yml`. Con tres filas de entrada inventadas (`2024/25`, `2024-2025`,
`2025-2026`) espera dos temporadas con su primer y último partido.
Ejecución: `dbt test --select slv_api_laliga__temporadas,test_type:unit`.

## 2. Documentación

- Descripción de cada modelo y de sus columnas clave en los `_<sistema>__models.yml`.
- Docs block `posicion` en `models/silver/rrhh/_rrhh__docs.md` (`{{ doc("posicion") }}`), reutilizable en gold.
- `dbt docs generate` genera la documentación navegable con descripciones, tests y linaje.

## 3. Paquetes

`packages.yml` con `dbt-labs/dbt_utils` (`>=1.3.0, <2.0.0`), versión fijada en `package-lock.yml`.
Se usa para `generate_surrogate_key`, `accepted_range` y `unique_combination_of_columns`.

## 4. Macros (`macros/`)

| Macro | SQL que genera | Uso |
|-------|----------------|-----|
| `limpiar_fecha(columna)` | `coalesce(try_to_date(x, 'YYYY-MM-DD'), try_to_date(x, 'DD/MM/YYYY'))` | 8 columnas de fecha en 5 modelos de staging |
| `normalizar_nombre(columna)` | `translate(upper(x), 'ÀÁÃ…', 'AAA…')` | Los dos lados del cruce jugador-informe en scouting |

Criterio: solo se crea una macro cuando la misma lógica se repite en varios modelos y `dbt_utils` no
la ofrece. Las columnas de fecha que llegan siempre en un único formato usan `try_to_date` directo.

## 5. Lo que no se ha usado y por qué

| Funcionalidad | Motivo |
|---------------|--------|
| Test genérico propio | Las reglas del proyecto quedan cubiertas por los tests de dbt y dbt_utils |
| `store_failures` | No necesario para el caso de uso |
| `generate_schema_name` personalizado | El comportamiento por defecto (`<schema_usuario>_<esquema>`) evita pisar tablas en desarrollo |
| `dbt_utils.star`, `run_query` | No hay columnas ni SQL que se generen dinámicamente |
| Streams y tasks de Snowflake | La carga incremental se resuelve con un modelo incremental de dbt |
