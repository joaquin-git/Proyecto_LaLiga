-- =============================================================================
-- 00_usuario_dbt.sql
-- Rol y usuario técnico para que dbt Cloud se conecte a Snowflake.
-- Ejecutar UNA vez con un usuario ACCOUNTADMIN (o SECURITYADMIN + SYSADMIN).
-- Antes, ejecuta la parte de 01_bronze_ddl_y_carga.sql que crea WH_LALIGA y LALIGA_DB,
-- o ejecuta este script después de ese.
-- =============================================================================
USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS DBT_ROLE COMMENT = 'Rol con el que dbt construye SILVER y GOLD';
GRANT ROLE DBT_ROLE TO ROLE SYSADMIN;

-- Cambia la contraseña. (En un proyecto real: autenticación con key pair).
CREATE USER IF NOT EXISTS DBT_USER
  PASSWORD = 'CambiaEstaPassword_2026!'
  DEFAULT_ROLE = DBT_ROLE
  DEFAULT_WAREHOUSE = WH_LALIGA
  MUST_CHANGE_PASSWORD = FALSE
  COMMENT = 'Usuario técnico de dbt Cloud';
GRANT ROLE DBT_ROLE TO USER DBT_USER;
-- Para que tú también puedas usar el rol desde Snowsight:
-- GRANT ROLE DBT_ROLE TO USER <TU_USUARIO>;

USE ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE WH_LALIGA TO ROLE DBT_ROLE;
GRANT USAGE ON DATABASE LALIGA_DB TO ROLE DBT_ROLE;

-- BRONZE: solo lectura
GRANT USAGE ON SCHEMA LALIGA_DB.BRONZE TO ROLE DBT_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA LALIGA_DB.BRONZE TO ROLE DBT_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA LALIGA_DB.BRONZE TO ROLE DBT_ROLE;

-- SILVER y GOLD: dbt crea y reemplaza objetos
GRANT ALL ON SCHEMA LALIGA_DB.SILVER TO ROLE DBT_ROLE;
GRANT ALL ON SCHEMA LALIGA_DB.GOLD TO ROLE DBT_ROLE;
-- dbt crea esquemas de desarrollo propios (p. ej. DBT_JOAQUIN):
GRANT CREATE SCHEMA ON DATABASE LALIGA_DB TO ROLE DBT_ROLE;

-- Cortex AI (AI_COMPLETE, AI_CLASSIFY, AI_FILTER) para la capa GOLD
USE ROLE ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE DBT_ROLE;
-- Si tu región no tiene el modelo que usemos, activa la inferencia entre regiones:
-- ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
