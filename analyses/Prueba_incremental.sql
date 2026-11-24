-- Demo del incremental en cadena con un jugador del Betis.
-- Sergi Altimira (OPT-92422) en el partido LL-00680 de la 2025/26:
-- la fila del partido en silver y su total de la temporada en gold.

with altimira as (

    select jugador_id
    from {{ ref('slv_rrhh__jugadores') }}
    where jugador_proveedor_id = 'OPT-92422'

)

select
      'silver · partido LL-00680'                       as capa
    , a.asistencias
    , a.fecha_extraccion::varchar                       as ultima_extraccion_o_carga
    , (select count(*)
       from {{ ref('slv_proveedor_estadisticas__actuaciones') }}) as filas_silver
from {{ ref('slv_proveedor_estadisticas__actuaciones') }} a
where a.partido_id = 'LL-00680'
  and a.jugador_id in (select jugador_id from altimira)

union all

select
      'gold · temporada 2025/26'
    , r.asistencias
    , r.fecha_ultima_carga::varchar
    , null
from {{ ref('fct_rendimiento_temporada') }} r
where r.temporada_id = '2025/26'
  and r.jugador_id in (select jugador_id from altimira)
