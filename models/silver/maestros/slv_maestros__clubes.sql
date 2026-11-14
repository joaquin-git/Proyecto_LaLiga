with alias as (

    select * from {{ ref('alias_clubes') }}

),

partidos     as (select * from {{ ref('stg_api_laliga__partidos') }}),
estadisticas as (select * from {{ ref('stg_proveedor_estadisticas__estadisticas_jugador_partido') }}),
contratos    as (select * from {{ ref('stg_rrhh__contratos') }}),
lesiones     as (select * from {{ ref('stg_servicios_medicos__lesiones') }}),
informes     as (select * from {{ ref('stg_app_scouting__informes_scouting') }}),
traspasos    as (select * from {{ ref('stg_mercado__traspasos') }}),
ligas        as (select * from {{ ref('slv_maestros__ligas') }}),

nombres_origen as (

    -- Todos los nombres de club, tal como vienen en las 6 fuentes.
    select equipo_local       as nombre from partidos
    union select equipo_visitante      from partidos
    union select equipo                from estadisticas
    union select rival                 from estadisticas
    union select equipo                from contratos
    union select club_propietario      from contratos
    union select equipo                from lesiones
    union select equipo_jugador        from informes
    union select club_origen           from traspasos
    union select club_destino          from traspasos

),

nombres_oficiales as (

    -- El seed traduce los alias ("Barça", "Atleti"...) al nombre oficial.
    -- Si un nombre no está en el seed (clubes extranjeros), se queda como viene.
    select distinct
          coalesce(a.nombre_oficial_club, n.nombre) as nombre_club
    from nombres_origen n
    left join alias a
      on n.nombre = a.alias_club
    where n.nombre is not null

),

clubes_laliga as (

    select distinct nombre_oficial_club as nombre_club from alias

),

ciudades as (

    -- Solo RRHH sabe la ciudad, y solo de los clubes de LaLiga.
    select distinct equipo as nombre_club, ciudad_equipo as ciudad from contratos

),

liga_club_externo as (

    -- La liga de los clubes extranjeros sale de los traspasos.
    select club_origen  as nombre_club, liga_origen  as nombre_liga from traspasos
    union
    select club_destino as nombre_club, liga_destino as nombre_liga from traspasos

),

clubes as (

    select
          o.nombre_club
        , c.ciudad
        , case
              when l.nombre_club is not null then 'LaLiga EA Sports'
              else e.nombre_liga
          end                                       as nombre_liga
    from nombres_oficiales o
    left join clubes_laliga l      on o.nombre_club = l.nombre_club
    left join ciudades c           on o.nombre_club = c.nombre_club
    left join liga_club_externo e  on o.nombre_club = e.nombre_club

)

select
      md5(cl.nombre_club)                           as club_id
    , cl.nombre_club
    , cl.ciudad
    , lg.liga_id
from clubes cl
left join ligas lg
  on cl.nombre_liga = lg.nombre_liga