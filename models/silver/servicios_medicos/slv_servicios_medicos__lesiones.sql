with lesiones as (

    select * from {{ ref('stg_servicios_medicos__lesiones') }}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

tipos as (

    select * from {{ ref('slv_servicios_medicos__tipos_lesion') }}

),

normalizado as (

    select
          l.lesion_id
        -- Los servicios médicos sí tienen la licencia: cruce directo con el jugador
        , l.codigo_licencia                                     as jugador_id
        , coalesce(a.nombre_oficial_club, l.equipo)             as nombre_club
        , trim(l.tipo_lesion)                                   as nombre_tipo_lesion
        -- "ISQUIOTIBIALES" / "isquiotibiales" -> "Isquiotibiales"
        , initcap(lower(l.zona_corporal))                       as zona_corporal
        , l.fecha_lesion
        -- 21 lesiones no traen fecha de alta: se calcula con los días de baja
        , coalesce(l.fecha_alta, dateadd(day, l.dias_baja, l.fecha_lesion))
                                                                as fecha_alta
        , l.partidos_perdidos
        , l.parte_medico
        , l.fecha_extraccion
    from lesiones l
    left join alias a on l.equipo = a.alias_club

)

select
      n.lesion_id
    , n.jugador_id
    , c.club_id
    , t.tipo_lesion_id
    , n.zona_corporal
    , n.fecha_lesion
    , n.fecha_alta
    , n.partidos_perdidos
    , n.parte_medico
    , n.fecha_extraccion
from normalizado n
left join clubes c on n.nombre_club        = c.nombre_club
left join tipos  t on n.nombre_tipo_lesion = t.nombre_tipo_lesion