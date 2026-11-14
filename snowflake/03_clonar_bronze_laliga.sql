-- =============================================================================
-- 03 · Bronze para PRE y PRO (zero-copy clone) y permisos de lectura
-- =============================================================================
-- Un clon no duplica el almacenamiento al crearse: comparte los datos con el
-- original y solo ocupa espacio lo que cambie después. Es la forma más barata
-- de tener la misma Bronze en los tres entornos.
-- Los permisos sobre la database original no pasan al clon: se conceden aquí
-- para los tres entornos.
-- Ejecutar DESPUÉS de cargar DEV_LALIGA_BRONZE_DB (script 02). Si se recarga
-- DEV, hay que volver a ejecutar este script.
-- =============================================================================

use role sysadmin;
create or replace database PRE_LALIGA_BRONZE_DB clone DEV_LALIGA_BRONZE_DB;
create or replace database PRO_LALIGA_BRONZE_DB clone DEV_LALIGA_BRONZE_DB;

-- Lectura de Bronze: cada rol, solo la de su entorno
use role securityadmin;
grant usage on database DEV_LALIGA_BRONZE_DB to role DEV_LALIGA_TRANSFORM_ROLE;
grant usage on all schemas in database DEV_LALIGA_BRONZE_DB to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in database DEV_LALIGA_BRONZE_DB to role DEV_LALIGA_TRANSFORM_ROLE;

grant usage on database PRE_LALIGA_BRONZE_DB to role PRE_LALIGA_TRANSFORM_ROLE;
grant usage on all schemas in database PRE_LALIGA_BRONZE_DB to role PRE_LALIGA_TRANSFORM_ROLE;
grant select on all tables in database PRE_LALIGA_BRONZE_DB to role PRE_LALIGA_TRANSFORM_ROLE;

grant usage on database PRO_LALIGA_BRONZE_DB to role PRO_LALIGA_TRANSFORM_ROLE;
grant usage on all schemas in database PRO_LALIGA_BRONZE_DB to role PRO_LALIGA_TRANSFORM_ROLE;
grant select on all tables in database PRO_LALIGA_BRONZE_DB to role PRO_LALIGA_TRANSFORM_ROLE;

-- Comprobación con el rol de desarrollo: debe devolver 767
use role DEV_LALIGA_TRANSFORM_ROLE;
use warehouse WH_LALIGA;
select count(*) from DEV_LALIGA_BRONZE_DB.api_laliga.partidos;

-- Aislamiento: sin roles secundarios, el rol de DEV NO debe poder leer PRO (tiene que dar error)
use secondary roles none;
select count(*) from PRO_LALIGA_BRONZE_DB.rrhh.contratos;
