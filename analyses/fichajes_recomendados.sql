select nombre_jugador, posicion_observada, club_actual,
       round(salario_actual_eur / 1000000, 2) as salario_millones,
       informes_fichar, informes, nota_media
from {{ ref('agg_shortlist_fichajes') }}
where club_actual is not null
  and club_actual <> 'Real Betis Balompié'
order by informes_fichar desc, nota_media desc