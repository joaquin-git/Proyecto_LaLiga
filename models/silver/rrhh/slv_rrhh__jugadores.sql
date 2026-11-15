with contratos as (

    select * from {{ ref('stg_rrhh__contratos') }}

),

estadisticas as (

    select * from {{ ref('stg_proveedor_estadisticas__estadisticas_jugador_partido') }}

),

jugadores as (

    -- RRHH es la fuente maestra del jugador: lo identifica con su licencia.
    -- Un jugador tiene varios contratos; nos quedamos con una fila por licencia.
    select
          codigo_licencia                               as jugador_id
        , nombre_jugador
        , fecha_nacimiento
        , case posicion
              when 'Portero'        then 'POR'
              when 'Defensa'        then 'DEF'
              when 'Centrocampista' then 'MED'
              when 'Delantero'      then 'DEL'
          end                                           as posicion
    from contratos
    qualify row_number() over (
        partition by codigo_licencia
        order by fecha_inicio desc
    ) = 1

),

ids_proveedor as (

    -- El proveedor identifica al jugador con su propio código.
    -- Para cruzarlo usamos nombre (en mayúsculas) + fecha de nacimiento:
    -- solo el nombre no basta porque hay homónimos (dos "Juan Cruz").
    select distinct
          jugador_proveedor_id
        , upper(nombre_jugador)                         as nombre_normalizado
        , fecha_nacimiento
    from estadisticas

),

final as (

    select
          j.jugador_id
        , p.jugador_proveedor_id
        , j.nombre_jugador
        , j.fecha_nacimiento
        , j.posicion
    from jugadores j
    left join ids_proveedor p
      on upper(j.nombre_jugador) = p.nombre_normalizado
     and j.fecha_nacimiento      = p.fecha_nacimiento

)

select * from final