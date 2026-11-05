-- =============================================================================
-- 02 · Carga de Bronze desde los CSV de data/bronze
--      (GENERADO por scripts/generar_bronze.py - no editar a mano)
-- =============================================================================
-- Simula lo que haría la herramienta de ingesta (Fivetran): deja los datos
-- crudos de las 6 fuentes del proyecto en DEV_LALIGA_BRONZE_DB. Pasos:
--   1. Ejecuta la parte A (crea stage, formato de fichero y tablas).
--   2. Sube los 6 CSV de data/bronze al stage DEV_LALIGA_BRONZE_DB.public.carga_bronze
--      desde Snowsight: abre el stage CARGA_BRONZE en el explorador de
--      databases y usa el botón para añadir ficheros.
--   3. Ejecuta la parte B (COPY INTO), los permisos y la comprobación final.
--
-- Diferencia con el script del curso: aquí TODAS las columnas de negocio son
-- varchar. Nuestras fuentes llegan sucias ("6,8", "42M€", "16/08/2024"...) y en
-- bronze no se puede rechazar ni perder ninguna fila: el tipado se hace en silver.
--
-- _loaded_at: cada tabla tiene una columna con DEFAULT current_timestamp(). El
-- COPY INTO no la menciona, así que Snowflake la rellena con el momento de la
-- carga. dbt la usa como loaded_at_field para el freshness. _fecha_extraccion,
-- en cambio, conserva la fecha en que el sistema de origen exportó la fila
-- (equivale a _fivetran_synced).
-- =============================================================================

use role sysadmin;
use warehouse WH_LALIGA;

-- =================================== PARTE A =================================
create stage if not exists DEV_LALIGA_BRONZE_DB.public.carga_bronze
    comment = 'Ficheros CSV para la carga inicial de Bronze (proyecto LaLiga)';

create file format if not exists DEV_LALIGA_BRONZE_DB.public.csv_bronze
    type = csv
    skip_header = 1
    field_optionally_enclosed_by = '"'
    null_if = ('')
    empty_field_as_null = true;

create or replace table DEV_LALIGA_BRONZE_DB.api_laliga.partidos (
      id_partido               varchar
    , temporada                varchar
    , jornada                  varchar
    , fecha_partido            varchar
    , hora                     varchar
    , equipo_local             varchar
    , equipo_visitante         varchar
    , estadio                  varchar
    , ciudad_estadio           varchar
    , aforo_estadio            varchar
    , goles_local              varchar
    , goles_visitante          varchar
    , resultado                varchar
    , espectadores             varchar
    , arbitro                  varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

create or replace table DEV_LALIGA_BRONZE_DB.proveedor_estadisticas.estadisticas_jugador_partido (
      id_partido               varchar
    , temporada                varchar
    , fecha_partido            varchar
    , id_jugador_proveedor     varchar
    , jugador                  varchar
    , fecha_nacimiento         varchar
    , nacionalidad             varchar
    , equipo                   varchar
    , rival                    varchar
    , condicion                varchar
    , posicion                 varchar
    , titular                  varchar
    , minutos                  varchar
    , goles                    varchar
    , asistencias              varchar
    , tiros                    varchar
    , tiros_a_puerta           varchar
    , pases_intentados         varchar
    , pases_completados        varchar
    , recuperaciones           varchar
    , tarjetas_amarillas       varchar
    , tarjetas_rojas           varchar
    , valoracion               varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

create or replace table DEV_LALIGA_BRONZE_DB.rrhh.contratos (
      id_contrato              varchar
    , codigo_licencia          varchar
    , jugador                  varchar
    , fecha_nacimiento         varchar
    , nacionalidades           varchar
    , posicion                 varchar
    , equipo                   varchar
    , ciudad_equipo            varchar
    , tipo_contrato            varchar
    , club_propietario         varchar
    , fecha_inicio             varchar
    , fecha_fin_prevista       varchar
    , fecha_baja               varchar
    , estado_contrato          varchar
    , salario_bruto_anual_eur  varchar
    , clausula_rescision_eur   varchar
    , agente                   varchar
    , agencia_representacion   varchar
    , email_agencia            varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

create or replace table DEV_LALIGA_BRONZE_DB.mercado.traspasos (
      id_operacion             varchar
    , fecha_operacion          varchar
    , ventana                  varchar
    , jugador                  varchar
    , nacionalidad             varchar
    , posicion                 varchar
    , club_origen              varchar
    , liga_origen              varchar
    , pais_origen              varchar
    , club_destino             varchar
    , liga_destino             varchar
    , pais_destino             varchar
    , tipo_operacion           varchar
    , importe                  varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

create or replace table DEV_LALIGA_BRONZE_DB.servicios_medicos.lesiones (
      id_lesion                varchar
    , codigo_licencia          varchar
    , jugador                  varchar
    , equipo                   varchar
    , temporada                varchar
    , fecha_lesion             varchar
    , fecha_alta               varchar
    , tipo_lesion              varchar
    , zona_corporal            varchar
    , dias_baja                varchar
    , partidos_perdidos        varchar
    , medico_responsable       varchar
    , parte_medico             varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

create or replace table DEV_LALIGA_BRONZE_DB.app_scouting.informes_scouting (
      id_informe               varchar
    , fecha_informe            varchar
    , ojeador                  varchar
    , email_ojeador            varchar
    , zona_ojeador             varchar
    , jugador                  varchar
    , equipo_jugador           varchar
    , partido_observado        varchar
    , fecha_partido            varchar
    , posiciones_observadas    varchar
    , nota_global              varchar
    , informe                  varchar
    , _fecha_extraccion        timestamp_ntz
    , _loaded_at               timestamp_ltz default current_timestamp()
);

-- Antes de la parte B: comprueba que los 6 ficheros están en el stage
list @DEV_LALIGA_BRONZE_DB.public.carga_bronze;

-- =================================== PARTE B =================================
-- La lista de columnas excluye _loaded_at: así toma su DEFAULT.
copy into DEV_LALIGA_BRONZE_DB.api_laliga.partidos
    (id_partido, temporada, jornada, fecha_partido, hora, equipo_local, equipo_visitante, estadio, ciudad_estadio, aforo_estadio, goles_local, goles_visitante, resultado, espectadores, arbitro, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('api_laliga__partidos.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

copy into DEV_LALIGA_BRONZE_DB.proveedor_estadisticas.estadisticas_jugador_partido
    (id_partido, temporada, fecha_partido, id_jugador_proveedor, jugador, fecha_nacimiento, nacionalidad, equipo, rival, condicion, posicion, titular, minutos, goles, asistencias, tiros, tiros_a_puerta, pases_intentados, pases_completados, recuperaciones, tarjetas_amarillas, tarjetas_rojas, valoracion, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('proveedor_estadisticas__estadisticas_jugador_partido.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

copy into DEV_LALIGA_BRONZE_DB.rrhh.contratos
    (id_contrato, codigo_licencia, jugador, fecha_nacimiento, nacionalidades, posicion, equipo, ciudad_equipo, tipo_contrato, club_propietario, fecha_inicio, fecha_fin_prevista, fecha_baja, estado_contrato, salario_bruto_anual_eur, clausula_rescision_eur, agente, agencia_representacion, email_agencia, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('rrhh__contratos.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

copy into DEV_LALIGA_BRONZE_DB.mercado.traspasos
    (id_operacion, fecha_operacion, ventana, jugador, nacionalidad, posicion, club_origen, liga_origen, pais_origen, club_destino, liga_destino, pais_destino, tipo_operacion, importe, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('mercado__traspasos.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

copy into DEV_LALIGA_BRONZE_DB.servicios_medicos.lesiones
    (id_lesion, codigo_licencia, jugador, equipo, temporada, fecha_lesion, fecha_alta, tipo_lesion, zona_corporal, dias_baja, partidos_perdidos, medico_responsable, parte_medico, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('servicios_medicos__lesiones.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

copy into DEV_LALIGA_BRONZE_DB.app_scouting.informes_scouting
    (id_informe, fecha_informe, ojeador, email_ojeador, zona_ojeador, jugador, equipo_jugador, partido_observado, fecha_partido, posiciones_observadas, nota_global, informe, _fecha_extraccion)
from @DEV_LALIGA_BRONZE_DB.public.carga_bronze files = ('app_scouting__informes_scouting.csv')
file_format = (format_name = 'DEV_LALIGA_BRONZE_DB.public.csv_bronze');

-- ================================ PERMISOS ===================================
-- dbt (DEV_LALIGA_TRANSFORM_ROLE) solo LEE bronze. Hay que darlo después de crear
-- las tablas: "on all tables" afecta solo a las que ya existen.
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.api_laliga to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.app_scouting to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.mercado to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.proveedor_estadisticas to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.rrhh to role DEV_LALIGA_TRANSFORM_ROLE;
grant select on all tables in schema DEV_LALIGA_BRONZE_DB.servicios_medicos to role DEV_LALIGA_TRANSFORM_ROLE;

-- ============================== COMPROBACIÓN =================================
-- Resultado esperado con los datos del repo:
--   partidos 767 · estadisticas_jugador_partido 22793 · contratos 619 · traspasos 126 · lesiones 747 · informes_scouting 1056
select 'partidos' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.api_laliga.partidos union all
select 'estadisticas_jugador_partido' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.proveedor_estadisticas.estadisticas_jugador_partido union all
select 'contratos' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.rrhh.contratos union all
select 'traspasos' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.mercado.traspasos union all
select 'lesiones' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.servicios_medicos.lesiones union all
select 'informes_scouting' as tabla, count(*) as filas from DEV_LALIGA_BRONZE_DB.app_scouting.informes_scouting;
