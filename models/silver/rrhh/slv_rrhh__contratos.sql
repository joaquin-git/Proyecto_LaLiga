with contratos as (

    select * from {{ ref('stg_rrhh__contratos') }}

),

alias as (

    select * from {{ ref('alias_clubes') }}

),

clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

normalizado as (

    select
          c.*
        , coalesce(ae.nombre_oficial_club, c.equipo)            as nombre_club
        , coalesce(ap.nombre_oficial_club, c.club_propietario)  as nombre_club_propietario
    from contratos c
    left join alias ae on c.equipo           = ae.alias_club
    left join alias ap on c.club_propietario = ap.alias_club

),

final as (

    select
          n.contrato_id
        , n.codigo_licencia                                     as jugador_id
        , cl.club_id
        -- Solo en cesiones: el club al que pertenece el jugador (puede ser extranjero)
        , cp.club_id                                            as club_propietario_id
        , n.tipo_contrato
        , n.fecha_inicio
        , n.fecha_fin_prevista
        , n.fecha_baja
        , n.estado_contrato
        , n.salario_bruto_anual_eur
        , n.clausula_rescision_eur
        , n.fecha_extraccion
    from normalizado n
    left join clubes cl on n.nombre_club             = cl.nombre_club
    left join clubes cp on n.nombre_club_propietario = cp.nombre_club

)

select * from final