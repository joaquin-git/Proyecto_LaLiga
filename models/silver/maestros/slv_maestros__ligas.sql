with traspasos as (

    select * from {{ ref('stg_mercado__traspasos') }}

),

paises as (

    select * from {{ ref('slv_maestros__paises') }}

),

ligas as (

    -- Cada operación trae la liga de origen y la de destino, con su país.
    select liga_origen   as nombre_liga, pais_origen   as nombre_pais from traspasos
    union
    select liga_destino  as nombre_liga, pais_destino  as nombre_pais from traspasos

)

select
      md5(l.nombre_liga)                            as liga_id
    , l.nombre_liga
    , p.pais_id
from ligas l
join paises p
  on l.nombre_pais = p.nombre_pais