with partidos as (

    select * from {{ ref('stg_api_laliga__partidos') }}

),

estadios as (

    -- En bronze el estadio se repite en cada partido (desnormalizado).
    -- Aquí cada estadio aparece una sola vez (3FN).
    select distinct
          nombre_estadio
        , ciudad_estadio                            as ciudad
        , aforo_estadio                             as aforo
    from partidos

)

select
      md5(nombre_estadio)                           as estadio_id
    , nombre_estadio
    , ciudad
    , aforo
from estadios