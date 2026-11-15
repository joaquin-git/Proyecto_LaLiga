with contratos as (

    select * from {{ ref('stg_rrhh__contratos') }}

),

paises as (

    select * from {{ ref('slv_maestros__paises') }}

),

nacionalidades as (

    -- "Marruecos; España" -> dos filas (1FN).
    -- split_to_table devuelve también la posición (index): la primera es la principal.
    select distinct
          c.codigo_licencia                             as jugador_id
        , trim(n.value)                                 as nombre_pais
        , n.index = 1                                   as es_principal
    from contratos c,
         lateral split_to_table(c.nacionalidades, ';') n

)

select
      n.jugador_id
    , p.pais_id
    , n.es_principal
from nacionalidades n
join paises p
  on n.nombre_pais = p.nombre_pais