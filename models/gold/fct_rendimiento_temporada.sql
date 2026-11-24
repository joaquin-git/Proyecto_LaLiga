{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='rendimiento_id',
    on_schema_change='append_new_columns'
) }}

with actuaciones as (

    select * from {{ ref('slv_proveedor_estadisticas__actuaciones') }}

),

partidos as (

    select * from {{ ref('slv_api_laliga__partidos') }}

),

{% if is_incremental() %}
temporadas_afectadas as (

    -- Solo las temporadas con actuaciones cargadas después de la última ejecución.
    -- Se recalcula la temporada entera porque la mediana necesita a todos sus jugadores.
    select distinct p.temporada_id
    from actuaciones a
    join partidos p on a.partido_id = p.partido_id
    where a.fecha_carga > (select max(fecha_ultima_carga) from {{ this }})

),
{% endif %}

contratos as (

    select * from {{ ref('slv_rrhh__contratos') }}

),

jugadores as (

    select * from {{ ref('slv_rrhh__jugadores') }}

),

temporadas as (

    -- Ventana económica de cada temporada: del 1 de julio al 30 de junio
    select
          temporada_id
        , date_from_parts(to_number(left(temporada_id, 4)), 7, 1)          as inicio_temporada
        , date_from_parts(to_number(left(temporada_id, 4)) + 1, 6, 30)     as fin_temporada
    from {{ ref('slv_api_laliga__temporadas') }}

),

rendimiento as (

    -- Lo que hizo cada jugador con cada club en cada temporada
    select
          a.jugador_id
        , a.club_id
        , p.temporada_id
        , count(*)                          as partidos_jugados
        , sum(a.minutos)                    as minutos
        , sum(a.goles)                      as goles
        , sum(a.asistencias)                as asistencias
        , max(a.fecha_carga)                as fecha_ultima_carga
    from actuaciones a
    join partidos p on a.partido_id = p.partido_id
    {% if is_incremental() %}
    where p.temporada_id in (select temporada_id from temporadas_afectadas)
    {% endif %}
    group by a.jugador_id, a.club_id, p.temporada_id

),

salarios as (

    -- Lo que cobró con ese club en esa temporada: cada contrato, prorrateado
    -- por los días que estuvo vigente dentro de la temporada
    select
          c.jugador_id
        , c.club_id
        , t.temporada_id
        , sum(
              c.salario_bruto_anual_eur
            * (datediff(day,
                   greatest(c.fecha_inicio, t.inicio_temporada),
                   least(coalesce(c.fecha_baja, c.fecha_fin_prevista), t.fin_temporada)) + 1)
            / 365
          )                                 as salario_temporada_eur
    from contratos c
    join temporadas t
      on c.fecha_inicio <= t.fin_temporada
     and coalesce(c.fecha_baja, c.fecha_fin_prevista) >= t.inicio_temporada
    group by c.jugador_id, c.club_id, t.temporada_id

),

costes as (

    select
          r.jugador_id
        , r.club_id
        , r.temporada_id
        , j.posicion
        , r.partidos_jugados
        , r.minutos
        , r.goles
        , r.asistencias
        , r.fecha_ultima_carga
        , round(s.salario_temporada_eur, 2)                         as salario_temporada_eur
        -- Con pocos minutos el coste por minuto no es comparable
        , r.minutos >= {{ var('minutos_minimos') }}                 as cumple_minutos_minimos
        , case
              when r.minutos >= {{ var('minutos_minimos') }}
                  then round(s.salario_temporada_eur / r.minutos, 2)
          end                                                       as coste_por_minuto_eur
        , round(s.salario_temporada_eur / nullif(r.goles, 0), 2)    as coste_por_gol_eur
        , round(s.salario_temporada_eur / nullif(r.goles + r.asistencias, 0), 2)
                                                                    as coste_por_contribucion_eur
    from rendimiento r
    join jugadores j on r.jugador_id = j.jugador_id
    left join salarios s
           on r.jugador_id   = s.jugador_id
          and r.club_id      = s.club_id
          and r.temporada_id = s.temporada_id

)

select
      {{ dbt_utils.generate_surrogate_key(['jugador_id', 'club_id', 'temporada_id']) }}
                                                                    as rendimiento_id
    , jugador_id
    , club_id
    , temporada_id
    , partidos_jugados
    , minutos
    , goles
    , asistencias
    , salario_temporada_eur
    , cumple_minutos_minimos
    , coste_por_minuto_eur
    , coste_por_gol_eur
    , coste_por_contribucion_eur
    -- Columna del filtro incremental
    , fecha_ultima_carga
    -- La referencia de P1: el coste por minuto "normal" de su posición en LaLiga esa temporada
    , round(median(coste_por_minuto_eur) over (partition by posicion, temporada_id), 2)
                                                                    as mediana_posicion_eur
    -- < 1: rinde por encima de lo que cobra · > 1: por debajo
    , round(coste_por_minuto_eur
            / median(coste_por_minuto_eur) over (partition by posicion, temporada_id), 2)
                                                                    as indice_coste_vs_mediana
from costes