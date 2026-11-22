with lesiones as (

    select * from {{ ref('slv_servicios_medicos__lesiones') }}

),

tipos as (

    select * from {{ ref('slv_servicios_medicos__tipos_lesion') }}

),

contratos as (

    select * from {{ ref('slv_rrhh__contratos') }}

)

select
      l.lesion_id
    , l.jugador_id
    , l.club_id
    , l.fecha_lesion
    , l.fecha_alta
    -- Tipo y zona van en el hecho (dimensión degenerada): son 14 y 13 valores
    , t.nombre_tipo_lesion
    , l.zona_corporal
    , datediff(day, l.fecha_lesion, l.fecha_alta)                     as dias_baja
    , l.partidos_perdidos
    , c.salario_bruto_anual_eur
    -- Lo que el club paga al jugador mientras no puede jugar
    , round(c.salario_bruto_anual_eur / 365
            * datediff(day, l.fecha_lesion, l.fecha_alta), 2)         as coste_lesion_eur
from lesiones l
left join tipos t on l.tipo_lesion_id = t.tipo_lesion_id
-- El contrato vigente el día de la lesión, en ese club (sin el club, 4 lesiones se duplicarían)
left join contratos c
       on l.jugador_id = c.jugador_id
      and l.club_id    = c.club_id
      and l.fecha_lesion between c.fecha_inicio and coalesce(c.fecha_baja, c.fecha_fin_prevista)