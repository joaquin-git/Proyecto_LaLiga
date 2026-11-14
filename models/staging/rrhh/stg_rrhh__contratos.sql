with source as (

    select * from {{ source('rrhh', 'contratos') }}

),

renombrado as (

    select
          id_contrato                                           as contrato_id
        , codigo_licencia
        , trim(jugador)                                         as nombre_jugador
        , coalesce(
              try_to_date(fecha_nacimiento, 'YYYY-MM-DD')
            , try_to_date(fecha_nacimiento, 'DD/MM/YYYY')
          )                                                     as fecha_nacimiento
        , nacionalidades
        , posicion
        , trim(equipo)                                          as equipo
        , ciudad_equipo
        , tipo_contrato
        , trim(club_propietario)                                as club_propietario
        , coalesce(
              try_to_date(fecha_inicio, 'YYYY-MM-DD')
            , try_to_date(fecha_inicio, 'DD/MM/YYYY')
          )                                                     as fecha_inicio
        , try_to_date(fecha_fin_prevista, 'YYYY-MM-DD')         as fecha_fin_prevista
        , try_to_date(fecha_baja, 'YYYY-MM-DD')                 as fecha_baja
        , estado_contrato
        , try_to_decimal(regexp_replace(salario_bruto_anual_eur, '[^0-9]', ''), 14, 2)
                                                                as salario_bruto_anual_eur
        , try_to_decimal(regexp_replace(clausula_rescision_eur, '[^0-9]', ''), 14, 2)
                                                                as clausula_rescision_eur
        , agente
        , agencia_representacion
        , email_agencia
        , _fecha_extraccion                                     as fecha_extraccion
        , _loaded_at                                            as fecha_carga
    from source

)

select * from renombrado