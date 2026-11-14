with source as (

    select * from {{ source('api_laliga', 'partidos') }}

),

renombrado as (

    select
          id_partido                                            
        , temporada                                             as temporada_origen
        , try_to_number(jornada)                                as jornada
        , coalesce(
              try_to_date(fecha_partido, 'YYYY-MM-DD')
            , try_to_date(fecha_partido, 'DD/MM/YYYY')
          )                                                     as fecha_partido
        , try_to_time(hora)                                     as hora_inicio
        , trim(equipo_local)                                    as equipo_local
        , trim(equipo_visitante)                                as equipo_visitante
        , trim(estadio)                                         as nombre_estadio
        , trim(ciudad_estadio)                                  as ciudad_estadio
        , try_to_number(replace(aforo_estadio, '.', ''))        as aforo_estadio
        , try_to_number(goles_local)                            as goles_local
        , try_to_number(goles_visitante)                        as goles_visitante
        , resultado                                             as resultado_quiniela
        , try_to_number(espectadores)                           as espectadores
        , trim(arbitro)                                         as arbitro
        , _fecha_extraccion                                     as date_load
        , _loaded_at                                            as loaded_at
    from source

)

select * from renombrado