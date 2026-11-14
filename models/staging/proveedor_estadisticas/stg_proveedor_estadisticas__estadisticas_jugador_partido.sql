with source as (

    select * from {{ source('proveedor_estadisticas', 'estadisticas_jugador_partido') }}

),

renombrado as (

    select
          id_partido                                            as partido_id
        , id_jugador_proveedor                                  as jugador_proveedor_id
        , temporada                                             as temporada_origen
        , coalesce(
              try_to_date(fecha_partido, 'YYYY-MM-DD')
            , try_to_date(fecha_partido, 'DD/MM/YYYY')
          )                                                     as fecha_partido
        , trim(jugador)                                         as nombre_jugador
        , coalesce(
              try_to_date(fecha_nacimiento, 'YYYY-MM-DD')
            , try_to_date(fecha_nacimiento, 'DD/MM/YYYY')
          )                                                     as fecha_nacimiento
        , trim(nacionalidad)                                    as nacionalidad
        , trim(equipo)                                          as equipo
        , trim(rival)                                           as rival
        , condicion
        , posicion
        , case
              when upper(titular) in ('S', 'TRUE')  then true
              when upper(titular) in ('N', 'FALSE') then false
          end                                                   as es_titular
        , try_to_number(minutos)                                as minutos
        , try_to_number(goles)                                  as goles
        , try_to_number(asistencias)                            as asistencias
        , try_to_number(tiros)                                  as tiros
        , try_to_number(tiros_a_puerta)                         as tiros_a_puerta
        , try_to_number(pases_intentados)                       as pases_intentados
        , try_to_number(pases_completados)                      as pases_completados
        , try_to_number(recuperaciones)                         as recuperaciones
        , try_to_number(tarjetas_amarillas)                     as tarjetas_amarillas
        , try_to_number(tarjetas_rojas)                         as tarjetas_rojas
        , try_to_decimal(replace(valoracion, ',', '.'), 3, 1)   as valoracion
        , _fecha_extraccion                                     as fecha_extraccion
        , _loaded_at                                            as fecha_carga
    from source

)

select * from renombrado