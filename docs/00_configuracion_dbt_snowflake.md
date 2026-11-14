# Configuración: Snowflake + dbt Platform + GitHub

Seguimos la convención del curso (`{ENV}_BRONZE_DB`, `{ENV}_TRANSFORM_ROLE`...) añadiendo el prefijo
`LALIGA`, para no mezclarnos con las bases de datos del proyecto de clase si comparten cuenta.

## 1. Objetos de Snowflake

| Elemento | Nombre |
|----------|--------|
| Warehouse | `WH_LALIGA` (X-Small, `auto_suspend = 60`) |
| Bronze | `DEV_LALIGA_BRONZE_DB` (+ clones `PRE_LALIGA_BRONZE_DB` y `PRO_LALIGA_BRONZE_DB`) |
| Silver | `DEV_LALIGA_SILVER_DB` · `PRE_LALIGA_SILVER_DB` · `PRO_LALIGA_SILVER_DB` |
| Gold | `DEV_LALIGA_GOLD_DB` · `PRE_LALIGA_GOLD_DB` · `PRO_LALIGA_GOLD_DB` |
| Roles de dbt | `DEV_LALIGA_TRANSFORM_ROLE` · `PRE_LALIGA_TRANSFORM_ROLE` · `PRO_LALIGA_TRANSFORM_ROLE` |
| Rol de consumo | `LALIGA_REPORTING_ROLE` (lectura de gold para Power BI) |

Bronze tiene un esquema por sistema de origen: `api_laliga`, `proveedor_estadisticas`, `rrhh`,
`mercado`, `servicios_medicos` y `app_scouting`. En `PUBLIC` está la infraestructura de carga
(stage `CARGA_BRONZE` y formato `CSV_BRONZE`).

## 2. Scripts (ejecutar en este orden)

| Script | Qué hace |
|--------|----------|
| `snowflake/01_entorno_laliga.sql` | Warehouse, databases, esquemas de bronze, roles y permisos. Sustituir `<TU_USUARIO>` antes de ejecutar |
| `snowflake/02_bronze_laliga.sql` | Parte A (stage, formato y tablas) → subir los 6 CSV de `data/bronze/` al stage → Parte B (`COPY INTO`), permisos y comprobación |
| `snowflake/03_clonar_bronze_laliga.sql` | Clona bronze a PRE y PRO (*zero-copy clone*) y da lectura a cada rol en su entorno |
| Par de claves (worksheet de Python) | Genera el par de claves para dbt. No se guarda en el repo porque su salida contiene la clave privada |

Si se recarga `DEV_LALIGA_BRONZE_DB`, hay que volver a ejecutar el script 03.

**Clave de Snowflake:** el usuario comparte cuenta con el proyecto de clase. Snowflake admite dos
claves públicas por usuario: el proyecto de clase usa `rsa_public_key` y LaLiga `rsa_public_key_2`.

## 3. Conexión en dbt Platform (proyecto `Proyecto_LaLiga`)

| Campo | Valor |
|-------|-------|
| Account | `OKFXYDR-UU45277` |
| Autenticación | Key pair |
| Role | `DEV_LALIGA_TRANSFORM_ROLE` |
| Warehouse | `WH_LALIGA` |
| Database | `DEV_LALIGA_GOLD_DB` |
| Schema (credenciales de desarrollo) | `dbt_<usuario>` (p. ej. `dbt_jgarcia`) |

**Repositorio:** `joaquin-git/Proyecto_LaLiga`, conectado por *Git clone* con *deploy key* (con
permiso de escritura). Pendiente: la integración nativa con la app de GitHub, necesaria para los
jobs de CI en las pull requests (día 8 del curso).

## 4. Variables de entorno

Definidas en dbt Platform (Environments → Environment variables), sin valor por defecto: si falta
una, dbt da error en vez de escribir en la base de datos equivocada.

| Variable | Development | PRE (pendiente) | PRO (pendiente) |
|----------|-------------|-----------------|-----------------|
| `DBT_BRONZE_DB` | `DEV_LALIGA_BRONZE_DB` | `PRE_LALIGA_BRONZE_DB` | `PRO_LALIGA_BRONZE_DB` |
| `DBT_SILVER_DB` | `DEV_LALIGA_SILVER_DB` | `PRE_LALIGA_SILVER_DB` | `PRO_LALIGA_SILVER_DB` |
| `DBT_GOLD_DB` | `DEV_LALIGA_GOLD_DB` | `PRE_LALIGA_GOLD_DB` | `PRO_LALIGA_GOLD_DB` |

Se usan en `dbt_project.yml` y en los sources con `"{{ env_var('DBT_SILVER_DB') }}"`.

## 5. Dónde construye dbt cada cosa

Se usa el comportamiento por defecto de dbt para los esquemas: en desarrollo, `dbt_<usuario>` +
`_` + el esquema de la carpeta.

| Capa | Database | Esquema en desarrollo | Materialización |
|------|----------|-----------------------|-----------------|
| Sources (bronze) | `DBT_BRONZE_DB` | el de cada sistema (solo lectura) | — |
| Staging | `DBT_SILVER_DB` | `dbt_<usuario>_<sistema>` (p. ej. `dbt_jgarcia_rrhh`) | view |

Silver y gold se configurarán en `dbt_project.yml` cuando se creen sus modelos.

## 6. Estructura del proyecto dbt

```
models/
  staging/<sistema>/   _<sistema>__sources.yml   (declaración de bronze + freshness)
packages.yml           dbt_utils
package-lock.yml       versión exacta instalada (se versiona)
seeds/  snapshots/  tests/  analyses/  macros/
```

La estructura crece con cada fase del curso.

## 7. Comprobaciones

| Comando | Resultado esperado |
|---------|--------------------|
| `dbt debug` | Conexión OK, database `DEV_LALIGA_GOLD_DB`, schema `dbt_<usuario>` |
| `dbt deps` | Instala dbt_utils |
| `dbt ls --resource-type source` | Las 6 fuentes |
| `dbt test --select "source:*"` | 11 tests en PASS |
| `dbt source freshness` | WARN/ERROR: esperado, la carga es histórica y única |
