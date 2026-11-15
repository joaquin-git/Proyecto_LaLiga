with lesiones as (

    select * from {{ ref('stg_servicios_medicos__lesiones') }}

),

tipos as (

    select distinct trim(tipo_lesion) as nombre_tipo_lesion
    from lesiones

)

select
      {{ dbt_utils.generate_surrogate_key(['nombre_tipo_lesion']) }}                                   as tipo_lesion_id
    , nombre_tipo_lesion
from tipos