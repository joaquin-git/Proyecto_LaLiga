with traspasos as (

    select * from {{ ref('stg_mercado__traspasos') }}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

jugadores as (

    select * from {{ ref('slv_rrhh__jugadores') }}

),

normalizado as (

    select
          t.traspaso_id
        , t.fecha_operacion
        , t.nombre_jugador
        , coalesce(ao.nombre_oficial_club, t.club_origen)       as nombre_club_origen
        , coalesce(ad.nombre_oficial_club, t.club_destino)      as nombre_club_destino
        , t.tipo_operacion
        -- Regla de negocio: en libres, cesiones y fines de cesión no hay pago.
        -- En origen venían como "Libre", "Cesión", "0", vacío o "N/D"; aquí siempre 0.
        , case
              when t.tipo_operacion in ('Libre', 'Cesión', 'Fin de cesión') then 0
              else t.importe_eur
          end                                                   as importe_eur
        , t.fecha_extraccion
    from traspasos t
    left join alias ao on t.club_origen  = ao.alias_club
    left join alias ad on t.club_destino = ad.alias_club

),

final as (

    select
          n.traspaso_id
        -- Mercado no tiene la licencia: buscamos al jugador por su nombre.
        -- (Comprobado: ningún homónimo aparece en los traspasos.)
        , j.jugador_id
        , n.fecha_operacion
        , co.club_id                                            as club_origen_id
        , cd.club_id                                            as club_destino_id
        , n.tipo_operacion
        , n.importe_eur
        , n.fecha_extraccion
    from normalizado n
    left join jugadores j  on upper(n.nombre_jugador)  = upper(j.nombre_jugador)
    left join clubes    co on n.nombre_club_origen    = co.nombre_club
    left join clubes    cd on n.nombre_club_destino   = cd.nombre_club

)

select * from final