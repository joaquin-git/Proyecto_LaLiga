# Configuración: Snowflake + dbt Cloud + GitHub

Seguimos la **convención del curso** adaptada a nuestro proyecto, con el prefijo `LALIGA` para no mezclarnos con
las databases del proyecto de clase (`snowflake/01_entorno_laliga.sql`):

| Elemento | Nombre |
|----------|--------|
| Warehouse | `WH_LALIGA` |
| Databases | `DEV_LALIGA_BRONZE_DB` · `{DEV,PRE,PRO}_LALIGA_SILVER_DB` · `{DEV,PRE,PRO}_LALIGA_GOLD_DB` |
| Roles de dbt | `DEV_LALIGA_TRANSFORM_ROLE` · `PRE_LALIGA_TRANSFORM_ROLE` · `PRO_LALIGA_TRANSFORM_ROLE` |
| Usuario | tu propio usuario de la trial (en un proyecto real, un usuario de servicio) |

Dónde vive cada capa del proyecto LaLiga:

| Capa | Ubicación |
|------|-----------|
| Bronze | `DEV_LALIGA_BRONZE_DB.<sistema_origen>.<tabla>` (por ejemplo, `DEV_LALIGA_BRONZE_DB.RRHH.CONTRATOS`) |
| Silver | `{ENV}_LALIGA_SILVER_DB.<sistema_origen>.slv_<sistema>__<tabla>` |
| Gold | `{ENV}_LALIGA_GOLD_DB.LALIGA.dim_* / fct_*` |

## 1. Snowflake

1. Ejecuta `snowflake/01_entorno_laliga.sql` (cambia antes `<TU_USUARIO>`). Crea el warehouse, las
   7 databases, los roles y los permisos de lectura de bronze y de Cortex.
2. Carga bronze con `snowflake/02_bronze_laliga.sql`, siguiendo `docs/01_bronze.md`, apartado 4.
3. Tu **account identifier** tiene el formato `ORGNAME-ACCOUNTNAME` (por ejemplo,
   `OKFXYDR-UU45277`).

## 2. Conexión en dbt Cloud (proyecto `Proyecto_LaLiga`)

| Campo | Valor |
|-------|-------|
| Account | `OKFXYDR-UU45277` |
| Database | `DEV_LALIGA_SILVER_DB` |
| Warehouse | `WH_LALIGA` |
| Role | `DEV_LALIGA_TRANSFORM_ROLE` |

**Credenciales de desarrollo:** *Username and password* con tu usuario de Snowflake. Como
*Schema* pon `LALIGA` (solo se usa si un modelo no define su propio esquema). Target name:
`default`. Threads: `4`.

**Repositorio:** GitHub → `joaquin-git/Proyecto_LaLiga`. Deja *Project subdirectory* vacío, porque
`dbt_project.yml` está en la raíz. Si el IDE te ofrece *Initialize dbt project*, **no lo pulses**: el
proyecto ya existe.

Comprobación en el IDE:
```
dbt debug
dbt ls --resource-type source     # debe listar las 6 tablas de bronze
```

## 3. Cómo elige dbt la database según el entorno

- `dbt_project.yml` pone `+database: "{{ env_var('DBT_ENTORNO', 'DEV') }}_LALIGA_SILVER_DB"`, y lo mismo
  para GOLD y para las sources de BRONZE.
- En desarrollo no hace falta definir nada: por defecto es `DEV`.
- Cuando creemos los environments de despliegue en dbt Cloud, cada uno tendrá la variable
  `DBT_ENTORNO` = `PRE` o `PRO` y su rol `PRE_LALIGA_TRANSFORM_ROLE` / `PRO_LALIGA_TRANSFORM_ROLE`. Así **el mismo
  código despliega en los tres entornos** sin tocarlo.
- Las carpetas de silver (`models/silver/<sistema_origen>/`) usarán como esquema el nombre del
  sistema, igual que `sql_server_dbo` en el proyecto del curso.

## 4. Estructura de carpetas

```
models/
  bronze/   _bronze__sources.yml                 -> declara las 6 tablas de DEV_LALIGA_BRONZE_DB
  silver/   <sistema>/slv_<sistema>__<tabla>.sql (staging/ para limpieza intermedia)
  gold/     dim_*.sql, fct_*.sql
snapshots/  histórico SCD2 (contratos/salarios)
seeds/      catálogos pequeños (alias de clubes)
macros/     generate_schema_name.sql
```
