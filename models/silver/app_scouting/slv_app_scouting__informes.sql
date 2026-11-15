with informes as (

    select * from {{ ref('stg_app_scouting__informes_scouting') }}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

ojeadores as (

    select * from {{ ref('slv_app_scouting__ojeadores') }}

),

jugadores as (

    select * from {{ ref('slv_rrhh__jugadores') }}

),

contratos as (

    select * from {{ ref('slv_rrhh__contratos') }}

),

partidos as (

    select * from {{ ref('slv_api_laliga__partidos') }}

),

normalizado as (

    select
          i.informe_id
        , i.fecha_informe
        , lower(trim(i.email_ojeador))                          as email_ojeador
        -- La app escribe a veces sin tildes ("Brahim Diaz"): las quitamos para comparar
        , translate(upper(i.nombre_jugador),
                    'ÀÁÃÉÍÏÑÓÖØÚÜĆČĞŘŠȚ',
                    'AAAEIINOOOUUCCGRST')                       as nombre_normalizado
        , coalesce(a.nombre_oficial_club, i.equipo_jugador)     as nombre_club
        , i.fecha_partido
        , i.nota_global
        , i.texto_informe
        , i.fecha_extraccion
    from informes i
    left join alias a on i.equipo_jugador = a.alias_club

),

candidatos as (

    -- Cada jugador con cada uno de sus contratos: nombre (sin tildes), club y fechas
    select
          j.jugador_id
        , translate(upper(j.nombre_jugador),
                    'ÀÁÃÉÍÏÑÓÖØÚÜĆČĞŘŠȚ',
                    'AAAEIINOOOUUCCGRST')                       as nombre_normalizado
        , c.club_id
        , c.fecha_inicio
        , coalesce(c.fecha_baja, c.fecha_fin_prevista)          as fecha_fin
    from jugadores j
    join contratos c on j.jugador_id = c.jugador_id

)

select
      n.informe_id
    , o.ojeador_id
    , ca.jugador_id
    , p.partido_id
    , n.fecha_informe
    , n.nota_global
    , n.texto_informe
    , n.fecha_extraccion
from normalizado n
left join ojeadores o on n.email_ojeador = o.email_ojeador
left join clubes   cl on n.nombre_club   = cl.nombre_club
-- Nombre + club + fecha: así se distinguen los dos Juan Cruz
left join candidatos ca
       on n.nombre_normalizado = ca.nombre_normalizado
      and cl.club_id           = ca.club_id
      and n.fecha_partido between ca.fecha_inicio and ca.fecha_fin
-- El partido observado: ese día, jugando el club del jugador (en casa o fuera)
left join partidos p
       on n.fecha_partido = p.fecha_partido
      and cl.club_id in (p.club_local_id, p.club_visitante_id)