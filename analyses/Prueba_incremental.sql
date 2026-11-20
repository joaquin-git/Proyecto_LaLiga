select
      j.nombre_jugador
    , a.partido_id
    , a.goles
    , a.asistencias
    , a.fecha_extraccion
    , (select count(*) from {{ ref('slv_proveedor_estadisticas__actuaciones') }}) as total_filas
from {{ ref('slv_proveedor_estadisticas__actuaciones') }} a
join {{ ref('slv_rrhh__jugadores') }} j on a.jugador_id = j.jugador_id
where a.partido_id = 'LL-00397'
  and j.nombre_jugador = 'Kylian Mbappé'