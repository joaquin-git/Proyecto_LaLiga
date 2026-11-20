with dias as (

    -- Una fila por día, del 1-jul-2024 al 30-jun-2026 (end_date no se incluye)
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2024-07-01' as date)",
        end_date="cast('2026-07-01' as date)"
    ) }}

)

select
      cast(date_day as date)                                    as fecha
    , year(date_day)                                            as anio
    , month(date_day)                                           as mes
    , to_char(date_day, 'YYYY-MM')                              as anio_mes
    -- La temporada va de julio a junio
    , case
          when month(date_day) >= 7
              then to_varchar(year(date_day)) || '/' || right(to_varchar(year(date_day) + 1), 2)
          else to_varchar(year(date_day) - 1) || '/' || right(to_varchar(year(date_day)), 2)
      end                                                       as temporada
from dias