-- =============================================================================
-- 01 · Entorno Snowflake del proyecto Moneyball LaLiga
-- =============================================================================
-- Adaptación del script del curso a nuestro proyecto. Misma convención Cívica,
-- con el prefijo LALIGA para no mezclarse con las databases del proyecto de clase:
--   {ENV}_LALIGA_BRONZE_DB / {ENV}_LALIGA_SILVER_DB / {ENV}_LALIGA_GOLD_DB
--   {ENV}_LALIGA_TRANSFORM_ROLE      (ENV = DEV, PRE, PRO)
-- Antes de ejecutarlo, sustituye <TU_USUARIO> (consúltalo con select current_user();)
-- Ejecútalo entero en una worksheet de Snowsight: "Run all".
-- =============================================================================

-- 1. Warehouse: el más pequeño, con suspensión automática a los 60 s para no
--    gastar créditos de la trial mientras no se usa.
use role sysadmin;
create warehouse if not exists WH_LALIGA
    warehouse_size = 'XSMALL'
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true;

-- 2. Databases. Bronze se crea solo en DEV: PRE y PRO serán clones (script 03).
--    En bronze, un schema por sistema de origen (igual que sql_server_dbo en el curso).
create database if not exists DEV_LALIGA_BRONZE_DB;
create schema if not exists DEV_LALIGA_BRONZE_DB.api_laliga;              -- calendario y resultados
create schema if not exists DEV_LALIGA_BRONZE_DB.proveedor_estadisticas;  -- estadísticas por partido
create schema if not exists DEV_LALIGA_BRONZE_DB.rrhh;                    -- contratos y salarios
create schema if not exists DEV_LALIGA_BRONZE_DB.mercado;                 -- traspasos y cesiones
create schema if not exists DEV_LALIGA_BRONZE_DB.servicios_medicos;       -- lesiones
create schema if not exists DEV_LALIGA_BRONZE_DB.app_scouting;            -- informes de ojeadores

create database if not exists DEV_LALIGA_SILVER_DB;
create database if not exists DEV_LALIGA_GOLD_DB;
create database if not exists PRE_LALIGA_SILVER_DB;
create database if not exists PRE_LALIGA_GOLD_DB;
create database if not exists PRO_LALIGA_SILVER_DB;
create database if not exists PRO_LALIGA_GOLD_DB;

-- 3. Roles de transformación: uno por entorno. dbt usa siempre el del entorno
--    en el que trabaja, y el de DEV no puede escribir en PRE ni en PRO.
use role securityadmin;
create role if not exists DEV_LALIGA_TRANSFORM_ROLE;
create role if not exists PRE_LALIGA_TRANSFORM_ROLE;
create role if not exists PRO_LALIGA_TRANSFORM_ROLE;

-- Rol de lectura para consumidores (Power BI leerá GOLD con este rol)
create role if not exists LALIGA_REPORTING_ROLE;

-- SYSADMIN hereda los roles funcionales
grant role DEV_LALIGA_TRANSFORM_ROLE to role sysadmin;
grant role PRE_LALIGA_TRANSFORM_ROLE to role sysadmin;
grant role PRO_LALIGA_TRANSFORM_ROLE to role sysadmin;
grant role LALIGA_REPORTING_ROLE to role sysadmin;

-- En la trial, tu usuario hará de desarrollador y de usuario de los jobs.
-- En un proyecto real, los jobs usan un usuario de servicio.
grant role DEV_LALIGA_TRANSFORM_ROLE to user <TU_USUARIO>;
grant role PRE_LALIGA_TRANSFORM_ROLE to user <TU_USUARIO>;
grant role PRO_LALIGA_TRANSFORM_ROLE to user <TU_USUARIO>;
grant role LALIGA_REPORTING_ROLE to user <TU_USUARIO>;

-- 4. Warehouse para los roles
grant usage on warehouse WH_LALIGA to role DEV_LALIGA_TRANSFORM_ROLE;
grant usage on warehouse WH_LALIGA to role PRE_LALIGA_TRANSFORM_ROLE;
grant usage on warehouse WH_LALIGA to role PRO_LALIGA_TRANSFORM_ROLE;
grant usage on warehouse WH_LALIGA to role LALIGA_REPORTING_ROLE;

-- 5. Cada rol puede crear schemas solo en las databases Silver y Gold de su
--    entorno. Quien crea un schema es su propietario: dbt podrá crear y
--    reemplazar tablas y vistas dentro sin más grants.
grant usage, create schema on database DEV_LALIGA_SILVER_DB to role DEV_LALIGA_TRANSFORM_ROLE;
grant usage, create schema on database DEV_LALIGA_GOLD_DB   to role DEV_LALIGA_TRANSFORM_ROLE;
grant usage, create schema on database PRE_LALIGA_SILVER_DB to role PRE_LALIGA_TRANSFORM_ROLE;
grant usage, create schema on database PRE_LALIGA_GOLD_DB   to role PRE_LALIGA_TRANSFORM_ROLE;
grant usage, create schema on database PRO_LALIGA_SILVER_DB to role PRO_LALIGA_TRANSFORM_ROLE;
grant usage, create schema on database PRO_LALIGA_GOLD_DB   to role PRO_LALIGA_TRANSFORM_ROLE;

-- 6. (Añadido) dbt necesita LEER bronze. Solo lectura: nunca escribe en él.
--    Los grants de SELECT sobre las tablas se dan en 02_bronze_laliga.sql, después de cargarlas.
use role sysadmin;
grant usage on database DEV_LALIGA_BRONZE_DB to role DEV_LALIGA_TRANSFORM_ROLE;
grant usage on all schemas in database DEV_LALIGA_BRONZE_DB to role DEV_LALIGA_TRANSFORM_ROLE;

-- 7. (Añadido) Cortex AI para la capa GOLD: AI_COMPLETE, AI_CLASSIFY, AI_FILTER.
use role accountadmin;
grant database role SNOWFLAKE.CORTEX_USER to role DEV_LALIGA_TRANSFORM_ROLE;
grant database role SNOWFLAKE.CORTEX_USER to role PRE_LALIGA_TRANSFORM_ROLE;
grant database role SNOWFLAKE.CORTEX_USER to role PRO_LALIGA_TRANSFORM_ROLE;
-- Si tu región no tiene el modelo que usemos, descomenta:
-- alter account set CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- Comprobación: deben aparecer las 7 databases
use role sysadmin;
show databases like '%LALIGA%_DB';
