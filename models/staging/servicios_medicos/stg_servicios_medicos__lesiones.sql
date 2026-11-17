with source as (

    select * from {{ source('servicios_medicos', 'lesiones') }}

),

renombrado as (

    select
          id_lesion                                             as lesion_id
        , codigo_licencia
        , trim(jugador)                                         as nombre_jugador
        , trim(equipo)                                          as equipo
        , temporada                                             as temporada_origen
        , {{ limpiar_fecha('fecha_lesion') }}                   as fecha_lesion
        , {{ limpiar_fecha('fecha_alta') }}                     as fecha_alta
        , tipo_lesion
        , trim(zona_corporal)                                   as zona_corporal
        , try_to_number(dias_baja)                              as dias_baja
        , try_to_number(partidos_perdidos)                      as partidos_perdidos
        , medico_responsable
        , parte_medico
        , _fecha_extraccion                                     as fecha_extraccion
        , _loaded_at                                            as fecha_carga
    from source

)

select * from renombrado