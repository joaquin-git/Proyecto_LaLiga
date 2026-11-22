with informes as (

    select * from {{ ref('fct_informes_scouting') }}

),

jugadores as (

    select * from {{ ref('dim_jugadores') }}

),

clubes as (

    select * from {{ ref('dim_clubes') }}

),

posiciones as (

    select * from {{ ref('slv_app_scouting__informe_posiciones') }}

),

contratos as (

    select * from {{ ref('slv_rrhh__contratos') }}

),

traspasos as (

    select * from {{ ref('slv_mercado__traspasos') }}

),

por_jugador as (

    -- Solo jugadores con al menos un informe que recomienda fichar
    select
          jugador_id
        , count(*)                                              as informes
        , count_if(recomendacion = 'Fichar')                    as informes_fichar
        , round(avg(nota_global), 1)                            as nota_media
    from informes
    group by jugador_id
    having count_if(recomendacion = 'Fichar') > 0

),

posicion_observada as (

    -- La posición principal que más veces anotan los ojeadores
    select
          i.jugador_id
        , mode(p.posicion_observada)                            as posicion_observada
    from informes i
    join posiciones p on i.informe_id = p.informe_id
    where p.es_principal
    group by i.jugador_id

),

contrato_actual as (

    -- Encaje económico 1: club y salario del contrato vigente más reciente
    select jugador_id, club_id, salario_bruto_anual_eur
    from contratos
    where fecha_baja is null
    qualify row_number() over (partition by jugador_id order by fecha_inicio desc) = 1

),

ultimo_traspaso as (

    -- Encaje económico 2: lo que se pagó por él la última vez
    select jugador_id, importe_eur, fecha_operacion
    from traspasos
    where tipo_operacion = 'Traspaso'
    qualify row_number() over (partition by jugador_id order by fecha_operacion desc) = 1

)

select
      p.jugador_id
    , j.nombre_jugador
    , j.posicion
    , po.posicion_observada
    , cl.nombre_club                                            as club_actual
    , ca.salario_bruto_anual_eur                                as salario_actual_eur
    , ut.importe_eur                                            as ultimo_traspaso_eur
    , ut.fecha_operacion                                        as fecha_ultimo_traspaso
    , p.informes
    , p.informes_fichar
    , p.nota_media
from por_jugador p
join jugadores j               on p.jugador_id = j.jugador_id
left join posicion_observada po on p.jugador_id = po.jugador_id
left join contrato_actual ca    on p.jugador_id = ca.jugador_id
left join clubes cl             on ca.club_id   = cl.club_id
left join ultimo_traspaso ut    on p.jugador_id = ut.jugador_id