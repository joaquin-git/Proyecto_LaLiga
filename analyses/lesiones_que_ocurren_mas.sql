select
      f.nombre_tipo_lesion
    , count(*)                                      as lesiones
    , round(sum(f.coste_lesion_eur) / 1000000, 2)   as coste_millones
from {{ ref('fct_lesiones') }} f
join {{ ref('dim_clubes') }} c on f.club_id = c.club_id
where c.nombre_club = 'Real Betis Balompié'
group by f.nombre_tipo_lesion
order by coste_millones desc