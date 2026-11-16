-- Los goles de los jugadores de cada equipo tienen que sumar el marcador del partido.
-- Cruza dos sistemas distintos: la API de partidos y el proveedor de estadísticas.
-- Entre 1 y 10 descuadres es un aviso (pueden ser goles en propia puerta,
-- que el proveedor no asigna a nadie); más de 10 es un error de datos.
{{ config(
    severity='error',
    warn_if='>0',
    error_if='>10'
) }}

with partidos as (

    select * from {{ ref('slv_api_laliga__partidos') }}

),

actuaciones as (

    select * from {{ ref('slv_proveedor_estadisticas__actuaciones') }}

),

marcador as (

    -- Una fila por partido y equipo, con los goles que dice el marcador
    select partido_id, club_local_id     as club_id, goles_local     as goles_marcador from partidos
    union all
    select partido_id, club_visitante_id as club_id, goles_visitante as goles_marcador from partidos

),

goles_jugadores as (

    select partido_id, club_id, sum(goles) as goles_jugadores
    from actuaciones
    group by partido_id, club_id

)

select
      m.partido_id
    , m.club_id
    , m.goles_marcador
    , coalesce(g.goles_jugadores, 0)    as goles_jugadores
from marcador m
left join goles_jugadores g
       on m.partido_id = g.partido_id
      and m.club_id    = g.club_id
where m.goles_marcador != coalesce(g.goles_jugadores, 0)