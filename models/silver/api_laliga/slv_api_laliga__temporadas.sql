with partidos as (

    select * from {{ ref('stg_api_laliga__partidos') }}

),

normalizado as (

    -- La API escribe la temporada de dos formas: '2024/25' y '2024-2025'.
    -- Las unificamos al formato corto '2024/25'.
    select
          case
              when temporada_origen like '____-____'
                  then left(temporada_origen, 4) || '/' || right(temporada_origen, 2)
              else temporada_origen
          end                                       as temporada_id
        , fecha_partido
    from partidos

),

temporadas as (

    select
          temporada_id
        , min(fecha_partido)                        as fecha_inicio
        , max(fecha_partido)                        as fecha_fin
    from normalizado
    group by temporada_id

)

select * from temporadas