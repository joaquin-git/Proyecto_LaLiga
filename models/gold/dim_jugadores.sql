with jugadores as (

select * from {{ ref('slv_rrhh__jugadores') }}

),

nacionalidades as (

select * from {{ ref('slv_rrhh__jugador_nacionalidades') }}

),

paises as (

select * from {{ ref('slv_maestros__paises') }}

),

nacionalidad_principal as (

-- En gold desnormalizamos: el nombre del país va dentro de la dimensión
select
 n.jugador_id
,p.nombre_pais as nacionalidad_principal
from nacionalidades n
join paises p on n.pais_id = p.pais_id
where n.es_principal
)

select
j.jugador_id
, j.nombre_jugador
, j.posicion
, j.fecha_nacimiento
, np.nacionalidad_principal
from jugadores j
left join nacionalidad_principal np on j.jugador_id = np.jugador_id