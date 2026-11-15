with informes as (

    select * from {{ ref('stg_app_scouting__informes_scouting') }}

)

-- "Lateral derecho, Central" -> dos filas (1FN). La primera es la principal.
select
      i.informe_id
    , trim(p.value)                                             as posicion_observada
    , p.index = 1                                               as es_principal
from informes i,
     lateral split_to_table(i.posiciones_observadas, ',') p