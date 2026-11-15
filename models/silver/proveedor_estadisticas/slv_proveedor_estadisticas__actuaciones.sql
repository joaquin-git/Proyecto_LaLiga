{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['partido_id', 'jugador_id']
) }}

with estadisticas as (

    select * from {{ ref('stg_proveedor_estadisticas__estadisticas_jugador_partido') }}
    {% if is_incremental() %}
      -- Solo lo que ha llegado a bronze después de la última carga
      where fecha_carga > (select max(fecha_carga) from {{ this }})
    {% endif %}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

jugadores as (

    select * from {{ ref('slv_rrhh__jugadores') }}

),

deduplicado as (

    -- El proveedor envió 160 filas repetidas. Además, el merge falla
    -- si en el mismo lote llegan dos filas con la misma clave.
    select *
    from estadisticas
    qualify row_number() over (
        partition by partido_id, jugador_proveedor_id
        order by fecha_extraccion desc
    ) = 1

),

final as (

    select
          d.partido_id
        -- El proveedor tiene su propio id; lo traducimos a la licencia
        , j.jugador_id
        -- Con qué club jugaba en ese partido
        , c.club_id
        , d.es_titular
        , d.minutos
        , d.goles
        , d.asistencias
        , d.tiros
        , d.tiros_a_puerta
        , d.pases_intentados
        , d.pases_completados
        , d.recuperaciones
        , d.tarjetas_amarillas
        , d.tarjetas_rojas
        , d.valoracion
        , d.fecha_extraccion
        -- Se queda: es la columna del filtro incremental
        , d.fecha_carga
    from deduplicado d
    left join jugadores j on d.jugador_proveedor_id = j.jugador_proveedor_id
    left join alias     a on d.equipo = a.alias_club
    left join clubes    c on coalesce(a.nombre_oficial_club, d.equipo) = c.nombre_club

)

select * from final