with informes as (

    select * from {{ ref('stg_app_scouting__informes_scouting') }}

),

ojeadores as (

    -- El ojeador se repetía en cada uno de sus informes: lo sacamos a su propia tabla
    select distinct
          nombre_ojeador
        , lower(trim(email_ojeador))                            as email_ojeador
        , trim(zona_ojeador)                                    as zona_ojeador
    from informes

)

select
      {{ dbt_utils.generate_surrogate_key(['email_ojeador']) }}                                        as ojeador_id
    , nombre_ojeador
    , email_ojeador
    , zona_ojeador
from ojeadores