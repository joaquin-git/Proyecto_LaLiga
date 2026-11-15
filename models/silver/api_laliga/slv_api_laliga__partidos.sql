with partidos as (

    select * from {{ ref('stg_api_laliga__partidos') }}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

estadios as (

    select * from {{ ref('slv_api_laliga__estadios') }}

),

deduplicado as (

    -- La API reenvía algunos partidos (7 repetidos). Nos quedamos con la versión
    -- más reciente de cada partido según la fecha de extracción.
    select *
    from partidos
    qualify row_number() over (
        partition by partido_id
        order by fecha_extraccion desc
    ) = 1

),

normalizado as (

    select
          d.partido_id
        -- Misma regla que en temporadas: '2024-2025' -> '2024/25'
        , case
              when d.temporada_origen like '____-____'
                  then left(d.temporada_origen, 4) || '/' || right(d.temporada_origen, 2)
              else d.temporada_origen
          end                                                   as temporada_id
        , d.jornada
        , d.fecha_partido
        , d.hora_inicio
        -- Nombre oficial del club: si el nombre está en el seed se traduce
        , coalesce(al.nombre_oficial_club, d.equipo_local)      as nombre_club_local
        , coalesce(av.nombre_oficial_club, d.equipo_visitante)  as nombre_club_visitante
        , d.nombre_estadio
        , d.goles_local
        , d.goles_visitante
        , d.espectadores
        , d.arbitro
        , d.fecha_extraccion
    from deduplicado d
    left join alias al on d.equipo_local     = al.alias_club
    left join alias av on d.equipo_visitante = av.alias_club

),

final as (

    -- Cambiamos los nombres por las claves de las tablas maestras
    select
          n.partido_id
        , n.temporada_id
        , n.jornada
        , n.fecha_partido
        , n.hora_inicio
        , cl.club_id                                            as club_local_id
        , cv.club_id                                            as club_visitante_id
        , e.estadio_id
        , n.goles_local
        , n.goles_visitante
        , n.espectadores
        , n.arbitro
        , n.fecha_extraccion
    from normalizado n
    left join clubes   cl on n.nombre_club_local     = cl.nombre_club
    left join clubes   cv on n.nombre_club_visitante = cv.nombre_club
    left join estadios e  on n.nombre_estadio        = e.nombre_estadio

)

select * from final