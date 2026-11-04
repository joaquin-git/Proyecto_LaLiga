# Configuración: Snowflake + dbt Cloud + GitHub

Orden recomendado: **Snowflake → dbt Cloud → conexión con este repositorio**.

## 1. Snowflake

1. En Snowsight, abre una hoja SQL y ejecuta `snowflake/01_bronze_ddl_y_carga.sql` hasta el
   `CREATE STAGE`. Esto crea el warehouse `WH_LALIGA`, la base de datos `LALIGA_DB` y los
   esquemas `BRONZE`, `SILVER` y `GOLD`.
2. Ejecuta `snowflake/00_usuario_dbt.sql`. Crea `DBT_ROLE` y `DBT_USER` (cambia la contraseña).
3. Sube los CSV y termina la carga de bronze: ver `docs/01_bronze.md`, apartado 4.
4. Apunta tu **account identifier**: Snowsight → menú de tu usuario (abajo a la izquierda) →
   *Account* → *View account details*. Tiene el formato `ORGNAME-ACCOUNTNAME`, por ejemplo
   `abcdefg-xy12345`.

## 2. Cuenta nueva de dbt Cloud

1. Regístrate en <https://www.getdbt.com/signup> con el plan **Developer** (gratuito, un proyecto).
2. Al crear el proyecto:
   - **Nombre:** `proyecto_laliga`.
   - **Conexión:** *Snowflake*.
     | Campo | Valor |
     |-------|-------|
     | Account | tu account identifier (`orgname-accountname`) |
     | Database | `LALIGA_DB` |
     | Warehouse | `WH_LALIGA` |
     | Role | `DBT_ROLE` |
   - **Credenciales de desarrollo:** usuario `DBT_USER`, su contraseña y, como *schema*,
     `DBT_<TUNOMBRE>`. Es tu esquema personal de desarrollo, donde dbt crea las tablas mientras
     trabajas en el IDE.
   - Pulsa **Test connection**.
3. **Repositorio:** elige *GitHub* → autoriza la app de dbt Cloud → selecciona
   `joaquin-git/Proyecto_LaLiga`.
   - El `dbt_project.yml` está en la **raíz** del repo, así que *Project subdirectory* se deja vacío.
4. Abre el **Studio IDE**. dbt no deja editar en `main`: crea una rama de trabajo (o usa la rama de
   este paso) y ejecuta:
   ```
   dbt debug
   dbt ls --resource-type source              # debe listar las 6 tablas de bronze
   ```

## 3. Cómo están organizados los esquemas

El macro `macros/generate_schema_name.sql` hace que:
- En **desarrollo** (IDE): todo se construye en tu esquema personal `DBT_<TUNOMBRE>`, para no
  pisar lo que ya funciona.
- En **producción** (un *job* con target `prod`): los modelos de `models/silver` van al esquema
  `SILVER` y los de `models/gold` al esquema `GOLD`.

Así se separan los entornos de desarrollo y producción, que es una de las buenas prácticas
(DataOps) que se ven en el curso.
