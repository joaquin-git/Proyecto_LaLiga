with contratos as (

    select nacionalidades from {{ ref('stg_rrhh__contratos') }}

),

estadisticas as (

    select nacionalidad from {{ ref('stg_proveedor_estadisticas__estadisticas_jugador_partido') }}

),

traspasos as (

    select nacionalidad, pais_origen, pais_destino from {{ ref('stg_mercado__traspasos') }}

),

nombres as (

    -- Las nacionalidades de RRHH vienen en una celda con varios valores ("Marruecos; España").
    -- split_to_table las separa en una fila por país (1FN).
    select trim(n.value)                            as nombre_pais
    from contratos c, lateral split_to_table(c.nacionalidades, ';') n

    union select trim(nacionalidad)  from estadisticas
    union select trim(nacionalidad)  from traspasos
    union select trim(pais_origen)   from traspasos
    union select trim(pais_destino)  from traspasos

)

select
      md5(nombre_pais)                              as pais_id
    , nombre_pais
from nombres
where nombre_pais is not null
  and nombre_pais <> ''