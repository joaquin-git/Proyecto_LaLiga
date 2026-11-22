select
      c.nombre_club
    , count(*)                                      as lesiones
    , round(sum(f.coste_lesion_eur) / 1000000, 2)   as coste_millones
from {{ ref('fct_lesiones') }} f
join {{ ref('dim_clubes') }} c on f.club_id = c.club_id
group by c.nombre_club
order by coste_millones desc