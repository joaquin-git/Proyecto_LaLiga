# Paso 4 · Capa SILVER (modelo entidad-relación)

## 1. Qué hace silver

Silver convierte las 6 tablas desnormalizadas de staging en un **modelo entidad-relación
normalizado**: cada dato vive en un único sitio, las entidades se relacionan por claves y se
eliminan duplicados, repeticiones y contradicciones.

- Modelos `slv_<sistema>__<entidad>`, materializados como `table` (una incremental).
- Database `{ENV}_LALIGA_SILVER_DB`; un esquema por sistema, más `maestros` para el dato maestro.
- Solo leen de staging, del seed o de otros modelos de silver (`ref()`), nunca de bronze.

## 2. Las 16 tablas

| Esquema | Tabla | Una fila es... | Filas | Clave |
|---------|-------|----------------|------:|-------|
| maestros | `slv_maestros__paises` | un país | 61 | `pais_id` |
| maestros | `slv_maestros__ligas` | una liga | 23 | `liga_id` |
| maestros | `slv_maestros__clubes` | un club (LaLiga o extranjero) | 85 | `club_id` |
| api_laliga | `slv_api_laliga__temporadas` | una temporada | 2 | `temporada_id` |
| api_laliga | `slv_api_laliga__estadios` | un estadio | 25 | `estadio_id` |
| api_laliga | `slv_api_laliga__partidos` | un partido | 760 | `partido_id` |
| rrhh | `slv_rrhh__jugadores` | un jugador | 470 | `jugador_id` (licencia) |
| rrhh | `slv_rrhh__jugador_nacionalidades` | un jugador y un país | 484 | `jugador_id` + `pais_id` |
| rrhh | `slv_rrhh__contratos` | un contrato o renovación | 619 | `contrato_id` |
| mercado | `slv_mercado__traspasos` | una operación de mercado | 126 | `traspaso_id` |
| servicios_medicos | `slv_servicios_medicos__tipos_lesion` | un tipo de lesión | 14 | `tipo_lesion_id` |
| servicios_medicos | `slv_servicios_medicos__lesiones` | una lesión | 747 | `lesion_id` |
| app_scouting | `slv_app_scouting__ojeadores` | un ojeador | 6 | `ojeador_id` |
| app_scouting | `slv_app_scouting__informes` | un informe | 1.056 | `informe_id` |
| app_scouting | `slv_app_scouting__informe_posiciones` | un informe y una posición | 1.370 | `informe_id` + `posicion_observada` |
| proveedor_estadisticas | `slv_proveedor_estadisticas__actuaciones` | un jugador en un partido | 22.633 | `partido_id` + `jugador_id` |

Claves sustitutas (países, ligas, clubes, estadios, tipos de lesión, ojeadores):
`dbt_utils.generate_surrogate_key` sobre el nombre (o el email del ojeador).

## 3. Relaciones

```
paises 1──N ligas 1──N clubes
clubes 1──N partidos (local) · clubes 1──N partidos (visitante) · estadios 1──N partidos · temporadas 1──N partidos
jugadores N──M paises            (jugador_nacionalidades)
jugadores 1──N contratos N──1 clubes   (y club_propietario en cesiones)
jugadores 1──N traspasos         (club_origen, club_destino)
jugadores 1──N lesiones N──1 tipos_lesion · lesiones N──1 clubes
ojeadores 1──N informes N──1 jugadores · informes N──1 partidos · informes 1──N informe_posiciones
partidos  1──N actuaciones N──1 jugadores · actuaciones N──1 clubes
```

## 4. Decisiones por bloque

### Dato maestro (`maestros`)
- **Clubes:** se recogen los nombres de las 6 fuentes, se traducen con el seed y se deja una fila por
  club real (los alias del Barça pasan a uno). La ciudad la aporta RRHH; la liga, mercado.
- **Países:** incluye las nacionalidades múltiples (`Marruecos; España`), separadas con
  `lateral split_to_table`.
- Clubes, países y ligas son entidades compartidas por todos los sistemas: por eso van en un esquema
  propio y no en el de ningún sistema (MDM).

### Partidos (`api_laliga`)
- **Deduplicado:** la API reenvió 7 partidos. Se conserva la versión más reciente con
  `qualify row_number() over (partition by partido_id order by fecha_extraccion desc) = 1` (767 → 760).
- **Temporadas:** `2024-2025` y `2024/25` se unifican en `2024/25`.
- **Estadios:** ciudad y aforo dependen del estadio, no del partido (3FN): tabla propia.
- **Roles:** dos claves a la misma tabla de clubes (`club_local_id`, `club_visitante_id`).

### Jugadores y contratos (`rrhh`)
- RRHH es la **fuente maestra del jugador**: la clave es la licencia, nunca el nombre (hay dos
  jugadores llamados Juan Cruz).
- El identificador del proveedor de estadísticas se obtiene cruzando nombre + fecha de nacimiento
  y se guarda en la tabla de jugadores (469 de 470; el que falta no jugó ningún minuto).
- Posición unificada a POR / DEF / MED / DEL.
- Una renovación es un contrato nuevo: se conserva el histórico de salarios.
- Nacionalidades: tabla puente N:M jugador-país (1FN), con la principal marcada.

### Traspasos (`mercado`)
- **Regla de negocio:** en Libre, Cesión y Fin de cesión el importe es 0 (en origen venía como texto,
  0, vacío o N/D).
- Mercado no tiene la licencia: el jugador se cruza por nombre. Comprobado que ningún homónimo aparece
  en los traspasos.

### Lesiones (`servicios_medicos`)
- Catálogo de tipos de lesión.
- `fecha_alta` que falta en origen (21) se calcula como `fecha_lesion + dias_baja`; después `dias_baja`
  se elimina por redundante. Suma total de días de baja comprobada: 14.951.
- Zona corporal unificada (35 escrituras → 13 zonas).
- `parte_medico` (texto libre) se conserva para Cortex en gold.

### Scouting (`app_scouting`)
- **Cruce con el jugador por nombre normalizado (sin tildes) + club + fecha del partido** contra el
  contrato vigente ese día: resuelve los nombres escritos sin tildes (57 informes) y los homónimos
  (los dos Juan Cruz aparecen en 6 informes). Resultado: 1.056 informes, ninguno sin jugador ni duplicado.
- El partido observado se busca por fecha + club del jugador (el texto libre del partido no se usa).
- Posiciones observadas (`Lateral derecho, Central`) separadas en una tabla propia (1FN).
- `texto_informe` se conserva para Cortex en gold.

### Actuaciones (`proveedor_estadisticas`): modelo incremental
- `materialized='incremental'`, `incremental_strategy='merge'`, `unique_key=['partido_id', 'jugador_id']`.
- Filtro: `fecha_carga > (select max(fecha_carga) from {{ this }})` (la columna existe en el destino).
- Deduplicado previo con `qualify` (160 filas repetidas; además el merge falla si un lote trae dos
  filas con la misma clave).
- Probado ejecutándolo dos veces y simulando una corrección del proveedor: la fila se actualiza sin
  duplicarse; `--full-refresh` reconstruye la tabla.
- Coherencia comprobada: los goles de las actuaciones (1.975) coinciden con los de los partidos.

## 5. Qué se queda en bronze y por qué

| Dato | Motivo |
|------|--------|
| Agente, agencia y email de la agencia | No responden a ninguna pregunta de negocio |
| Médico responsable | Depende del club, no de la lesión, y no se usa |
| Ventana de mercado, temporada de la lesión, días de baja | Se calculan a partir de las fechas |
| Nombres repetidos (jugador, club, estadio) en tablas de hechos | Ya están en su tabla (3FN) |
