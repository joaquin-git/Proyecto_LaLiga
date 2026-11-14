with source as (

    select * from {{ source('mercado', 'traspasos') }}

),

renombrado as (

    select
          id_operacion                                          as traspaso_id
        , coalesce(
              try_to_date(fecha_operacion, 'YYYY-MM-DD')
            , try_to_date(fecha_operacion, 'DD/MM/YYYY')
          )                                                     as fecha_operacion
        , ventana
        , trim(jugador)                                         as nombre_jugador
        , nacionalidad
        , posicion
        , trim(club_origen)                                     as club_origen
        , liga_origen
        , pais_origen
        , trim(club_destino)                                    as club_destino
        , liga_destino
        , pais_destino
        , tipo_operacion
        , case
              -- Libre y Cesión: importe 0
              when upper(trim(importe)) in ('LIBRE', 'CESIÓN', 'CESION') then 0
              -- N/D: no se conoce, se deja vacío (no es lo mismo que 0)
              when upper(trim(importe)) = 'N/D' then null
              -- En millones: 42M, 25,5M, 42M€
              when upper(importe) like '%M%'
                  then try_to_decimal(replace(regexp_replace(importe, '[^0-9,.]', ''), ',', '.'), 14, 2) * 1000000
              -- El resto: 42000000 o 42.000.000 €
              else try_to_decimal(regexp_replace(importe, '[^0-9]', ''), 14, 2)
          end                                                   as importe_eur
        , _fecha_extraccion                                     as fecha_extraccion
        , _loaded_at                                            as fecha_carga
    from source

)

select * from renombrado