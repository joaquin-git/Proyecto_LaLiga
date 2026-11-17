# Paso 3 · Seed y capa STAGING

## 1. Seed `alias_clubes`

Cada fuente escribe los clubes a su manera (`Barça`, `FC Barcelona`, `Barcelona`; `Atleti`,
`Atlético`...). El seed es una tabla pequeña y estable, versionada en Git, que traduce cada alias
al nombre oficial.

| Columna | Descripción |
|---------|-------------|
| `alias_club` | Nombre tal y como llega de alguna fuente (único) |
| `nombre_oficial_club` | Nombre oficial del club |

- 63 alias para los 23 clubes de LaLiga de las dos temporadas.
- Tipos fijados con `+column_types` en `dbt_project.yml` (`varchar(50)`).
- Tests: `unique` y `not_null` en `alias_club`, `not_null` en `nombre_oficial_club`.
- Se materializa en `{ENV}_LALIGA_SILVER_DB`, esquema `seeds`.
- Se usa con `ref('alias_clubes')` y `coalesce(alias.nombre_oficial_club, nombre_origen)`: si un nombre
  no tiene alias (ya es oficial, o es un club extranjero), se queda como está.

## 2. Sources

Un fichero `_<sistema>__sources.yml` por sistema de origen, en `models/staging/<sistema>/`.

- `database: "{{ env_var('DBT_BRONZE_DB') }}"`: la misma definición sirve para DEV, PRE y PRO.
- **Freshness** sobre `_loaded_at`: aviso a las 24 h y error a las 48 h. Con los datos de ejemplo
  (carga única) da error, que es lo esperado: en producción avisaría de que un sistema ha dejado de enviar.
- **Tests (11):** `not_null` en el identificador de las 6 tablas; `unique` en contratos, traspasos,
  lesiones e informes. En partidos y estadísticas no hay `unique` porque la fuente reenvía filas
  (7 partidos y 160 estadísticas duplicadas): se resuelve en silver.

## 3. Modelos de staging

Una vista por tabla de bronze (`stg_<sistema>__<tabla>`), en `{ENV}_LALIGA_SILVER_DB`, esquema del
sistema. **Solo renombra y castea**: no filtra, no deduplica y no cruza tablas (mismo número de filas que bronze).

Patrón de CTEs de todos los modelos:

```sql
with source as (
    select * from {{ source('api_laliga', 'partidos') }}
),
renombrado as (
    select ... from source
)
select * from renombrado
```

| Transformación | Ejemplo | Cómo |
|----------------|---------|------|
| Nombres en español y `entidad_id` | `id_partido` → `partido_id` | alias |
| Fechas en dos formatos | `2025-01-25` y `25/01/2025` | macro `limpiar_fecha` |
| Números con separador de miles | `40.000` → 40000 | `try_to_number(replace(x, '.', ''))` |
| Decimales con coma | `6,8` → 6.8 | `try_to_decimal(replace(x, ',', '.'), 3, 1)` |
| Importes con texto | `45.000.000 €`, `45M`, `Libre`, `N/D` | `regexp_replace` + `case` |
| Booleanos escritos de cuatro formas | `S`, `true`, `N`, `false` | `case` → boolean |
| Espacios sobrantes | `" Kylian Mbappé "` | `trim` |
| Metadatos | `_fecha_extraccion`, `_loaded_at` | → `fecha_extraccion`, `fecha_carga` |

Se usan las funciones `try_` (`try_to_date`, `try_to_number`, `try_to_decimal`...): si un valor no se
puede convertir devuelven NULL en lugar de romper la ejecución.

| Modelo | Filas |
|--------|------:|
| `stg_api_laliga__partidos` | 767 |
| `stg_proveedor_estadisticas__estadisticas_jugador_partido` | 22.793 |
| `stg_rrhh__contratos` | 619 |
| `stg_mercado__traspasos` | 126 |
| `stg_servicios_medicos__lesiones` | 747 |
| `stg_app_scouting__informes_scouting` | 1.056 |
