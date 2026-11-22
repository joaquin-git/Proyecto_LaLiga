with informes as (

    select * from {{ ref('slv_app_scouting__informes') }}

),

ojeadores as (

    select * from {{ ref('slv_app_scouting__ojeadores') }}

),

partidos as (

    select * from {{ ref('slv_api_laliga__partidos') }}

)

select
      i.informe_id
    , i.jugador_id
    , p.fecha_partido
    , o.nombre_ojeador
    , i.nota_global
    -- Regla de negocio: la recomendación final del ojeador está escrita en el texto
    , case
          when trim(i.texto_informe) ilike any (
                   '%fichar.%', '%ir a por él%', '%prioridad alta%', '%adelante con la operación%',
                   '%iniciar contactos%', '%moverse antes%', '%lo ficharía%')
              then 'Fichar'
          when trim(i.texto_informe) ilike any (
                   '%no interesa%', '% no.', '%descartad%', '%descartar.%', '%no lo recomiendo%',
                   '%no es jugador para nosotros%', '%no aporta nada%', '%no tiene sentido plantear%')
              then 'Descartar'
          else 'Seguir observando'
      end                                                           as recomendacion
    , i.texto_informe
from informes i
left join ojeadores o on i.ojeador_id = o.ojeador_id
left join partidos  p on i.partido_id = p.partido_id