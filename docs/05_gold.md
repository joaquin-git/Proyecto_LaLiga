# Paso 6 · Capa GOLD (modelo dimensional)

## 1. Qué hace gold

Silver está normalizado para que cada dato viva en un único sitio. Gold reorganiza esos datos
**pensando en quien consulta** (Power BI): un **modelo dimensional en estrella**, con tablas de
**hechos** (lo que se mide) rodeadas de **dimensiones** (el contexto por el que se corta).

Método seguido para cada pregunta de negocio: **grano → medidas → dimensiones**.

- Modelos en `models/gold/`, materializados como `table`, salvo `fct_rendimiento_temporada`, que es
  `incremental` (ver P1).
- Database `{ENV}_LALIGA_GOLD_DB`, esquema `gold` (`dbt_<usuario>_gold` en desarrollo).
- Power BI lee con `LALIGA_REPORTING_ROLE` (solo lectura).

## 2. Las 7 tablas

| Tabla | Tipo | Grano (una fila = ...) | Filas | Pregunta |
|-------|------|------------------------|------:|----------|
| `dim_jugadores` | Dimensión | un jugador | 470 | todas |
| `dim_clubes` | Dimensión | un club (con liga y país) | 85 | todas |
| `dim_fechas` | Dimensión | un día, de julio de 2024 a junio de 2026 | 730 | P2, P3 |
| `fct_rendimiento_temporada` | Hechos | un jugador en un club en una temporada | 779 | **P1** |
| `fct_lesiones` | Hechos | una lesión | 747 | **P2** |
| `fct_informes_scouting` | Hechos | un informe de un ojeador | 1.056 | **P3** |
| `agg_shortlist_fichajes` | Agregado | un candidato a fichar | 94 | **P3** |

```
                         dim_fechas
                        ▲          ▲
                        │          │
 dim_clubes ◄── fct_lesiones   fct_informes_scouting ──► dim_jugadores
     ▲                                                        ▲
     └────────── fct_rendimiento_temporada ───────────────────┘
                                         agg_shortlist_fichajes (desde fct_informes_scouting)
```

## 3. Decisiones por tabla

### Dimensiones
- **`dim_jugadores`** junta jugadores, nacionalidades y países (desnormaliza a propósito) con la
  posición y la nacionalidad principal. Reutiliza el docs block `posicion`.
- **`dim_clubes`** aplana la cadena club → liga → país de silver (copo de nieve → estrella) y añade
  `es_laliga` para filtrar.
- **`dim_fechas`** se genera con `dbt_utils.date_spine` (un día por fila aunque ese día no pase nada),
  con año, mes, año-mes y temporada (de julio a junio).
- `dim_jugadores` y `dim_clubes` tienen **contrato** (`contract: enforced`): dbt comprueba columnas y
  tipos antes de crear la tabla, para que un cambio no rompa el informe.

### P1 · `fct_rendimiento_temporada`
- **Grano jugador-club-temporada:** el salario es anual y un jugador puede cambiar de club a mitad
  de temporada.
- **Salario de la temporada prorrateado:** cada contrato cuenta por los días que estuvo vigente entre
  el 1 de julio y el 30 de junio (`greatest`/`least` para el solape), de modo que una renovación a
  mitad de temporada cuenta bien.
- **Coste por minuto** solo con un mínimo de minutos: `var('minutos_minimos')` = 900 (se cambia con
  `--vars` sin tocar código). Además, coste por gol y por contribución (goles + asistencias), con
  `nullif` para no dividir entre cero.
- **Referencia:** la mediana del coste por minuto de su posición en LaLiga **esa temporada** (función de
  ventana `median(...) over (partition by posicion, temporada_id)`), porque los sueldos suben de un año a
  otro. `indice_coste_vs_mediana` < 1 = rinde por encima de lo que cobra. Mediana y no media, para que
  unos pocos sueldos enormes no distorsionen.
- **Incremental en cadena:** `merge` por `rendimiento_id`. Si llegan actuaciones con `fecha_carga`
  posterior a la última ejecución (`fecha_ultima_carga`), recalcula **la temporada entera** afectada: la
  mediana necesita a todos los jugadores de la temporada. No detecta borrados ni cambios de contratos:
  para eso, `--full-refresh`.
- Medianas (€/min), 2024/25 → 2025/26: MED 674,55 → 749,37 · DEF 767,14 → 928,72 ·
  POR 908,73 → 778,89 · DEL 1.038,53 → 1.221,35.
- Betis 2025/26: Altimira 0,43 (renovar) · Isco 4,50 · Sabaly 2,99 (revisar). 9 de 33 temporadas de
  jugadores del Betis por debajo de la mediana.
- Comprobado: mismos minutos (1.504.710) y goles (1.975) que silver; ninguna fila sin salario.

### P2 · `fct_lesiones`
- **Coste = salario anual / 365 × días de baja**, con el contrato vigente ese día **en ese club**
  (sin el club, 4 lesiones encontraban un contrato antiguo sin cerrar y se duplicaban).
- Tipo de lesión y zona dentro de la tabla (**dimensión degenerada**: 14 y 13 valores).
- `fecha_lesion` enlaza con `dim_fechas` para agrupar por mes y temporada.
- Comprobado: 747 lesiones, 14.951 días de baja, ≈ 145,89 M€.

### P3 · `fct_informes_scouting` y `agg_shortlist_fichajes`
- **La recomendación se extrae del texto** con una regla de negocio (`case` + `ilike any`) sobre las
  frases con las que el ojeador cierra el informe: Fichar / Seguir observando / Descartar
  (185 / 506 / 365). La nota no sirve: mide el partido, no la decisión.
- **Shortlist:** jugadores con al menos un "Fichar", con su **encaje económico** (club y salario del
  contrato vigente, último traspaso pagado) y la posición más observada (`mode`).


## 4. Calidad, permisos y linaje

- **Tests:** claves `unique`/`not_null`, `relationships` de cada hecho hacia sus dimensiones
  (incluida `dim_fechas`), `accepted_values` en temporada y recomendación.
- **Permisos:** `+grants: select` a `LALIGA_REPORTING_ROLE` en `dbt_project.yml` (se aplica en cada
  construcción). El `usage` sobre la database y los esquemas futuros se dio una vez en Snowflake.
- **Exposure** `informe_moneyball_laliga` (`_gold__exposures.yml`): el informe de Power BI aparece
  al final del linaje y se puede construir todo lo que necesita con
  `dbt build --select +exposure:informe_moneyball_laliga`.
