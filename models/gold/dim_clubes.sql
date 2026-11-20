with clubes as (

    select * from {{ ref('slv_maestros__clubes') }}

),

ligas as (

    select * from {{ ref('slv_maestros__ligas') }}

),

paises as (

    select * from {{ ref('slv_maestros__paises') }}

)

-- Silver tenía club -> liga -> país en tres tablas; en gold va todo en una (estrella)
select
      c.club_id
    , c.nombre_club
    , c.ciudad
    , l.nombre_liga
    , p.nombre_pais
    , l.nombre_liga = 'LaLiga EA Sports'        as es_laliga
from clubes c
left join ligas  l on c.liga_id = l.liga_id
left join paises p on l.pais_id = p.pais_id