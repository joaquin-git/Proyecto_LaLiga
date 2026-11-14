with source as (

    select * from {{ source('app_scouting', 'informes_scouting') }}

),

renombrado as (

    select
          id_informe                                            as informe_id
        , try_to_timestamp(fecha_informe, 'YYYY-MM-DD HH24:MI') as fecha_informe
        , trim(ojeador)                                         as nombre_ojeador
        , email_ojeador
        , zona_ojeador
        , trim(jugador)                                         as nombre_jugador
        , trim(equipo_jugador)                                  as equipo_jugador
        , partido_observado
        , try_to_date(fecha_partido, 'YYYY-MM-DD')              as fecha_partido
        , posiciones_observadas
        , try_to_decimal(replace(nota_global, ',', '.'), 3, 1)  as nota_global
        , informe                                               as texto_informe
        , _fecha_extraccion                                     as fecha_extraccion
        , _loaded_at                                            as fecha_carga
    from source

)

select * from renombrado