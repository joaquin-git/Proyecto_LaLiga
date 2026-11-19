# Moneyball LaLiga ⚽ — eficiencia salarial de las plantillas

Proyecto de Data Engineering (formación Cívica) con **Snowflake + dbt + Cortex AI + Power BI**
sobre la liga española de fútbol masculino, temporadas **2024/25 y 2025/26**.

## El caso de uso (en una frase)

> **"¿Qué jugadores rinden más por cada euro que cobran, cuánto dinero perdemos con los lesionados
> y a quién deberíamos fichar?"**

**Cliente:** la Dirección Deportiva del **Real Betis Balompié**. Es un club de presupuesto medio
(7.º en masa salarial de LaLiga) con el límite de coste de plantilla ajustado: no puede gastar
mucho, así que tiene que gastar bien.

**Por qué usa los datos de toda la liga:** para comparar a sus jugadores con el precio de mercado
del rendimiento (P1), para comparar su coste de lesiones con el resto de clubes (P2) y porque los
fichajes que recomiendan sus ojeadores están en otros clubes (P3). El modelo sirve igual para
cualquier club: el club se elige con un filtro en Power BI.

### Preguntas de negocio que el modelo debe responder

| # | Pregunta | Ejemplo de respuesta (datos del proyecto) |
|---|----------|-------------------------------------------|
| P1 | ¿Cuánto nos cuesta cada minuto jugado, cada gol y cada asistencia de cada jugador? ¿Quién rinde por encima o por debajo de lo que cobra, comparado con la mediana de la liga en su posición? | "Sergi Altimira cuesta ≈ 323 € por minuto, la mitad que un centrocampista medio de LaLiga (≈ 692 €); Isco, ≈ 3.369 €, casi cinco veces más" |
| P2 | ¿Cuánto salario pagamos a jugadores lesionados (coste de enfermería) por tipo de lesión y mes, y cómo estamos frente al resto de clubes? | "El Betis pagó 4,68 M€ a lesionados en dos temporadas (4,4 % de su masa salarial, frente al 5,7 % de la liga); la lesión más cara, la rotura fibrilar de grado I (1,65 M€)" |
| P3 | ¿Qué jugadores de otros clubes recomiendan fichar nuestros ojeadores, y caben en nuestro presupuesto (salario actual y último traspaso)? | "La IA (Cortex) clasifica los 1.056 informes en Fichar / Seguir observando / Descartar, resume a cada candidato y muestra su salario y su último traspaso" |

## Arquitectura (medallion)

```
FUENTES (6 CSV)          BRONZE                          STAGING + SILVER                GOLD                            CONSUMO
API partidos      ─┐                                 modelo entidad-relación         modelo dimensional              Power BI
Proveedor stats   ─┤     copia fiel, todo VARCHAR    limpieza + normalización        hechos + dimensiones            (Copilot)
RRHH contratos    ─┼──►  + metadatos de carga   ──►  claves PK/FK, tipos         ──► Cortex: AI_CLASSIFY,       ──►
Mercado/traspasos ─┤     (COPY INTO)                 (dbt)                            AI_FILTER, AI_COMPLETE (dbt)
Servicio médico   ─┤
App scouting      ─┘
```

## Estructura del repositorio

| Carpeta / fichero | Contenido |
|---------|-----------|
| `data/bronze/` | Los 6 CSV de origen (generados) |
| `data/validacion/` | "Verdad" oculta para medir la precisión de la IA en gold (no se carga en bronze) |
| `scripts/` | Generador del dataset (`generar_bronze.py`) y datos maestros |
| `snowflake/` | Scripts de entorno (01), carga de bronze (02) y clones PRE/PRO (03) |
| `seeds/` | `alias_clubes`: tabla de equivalencias entre los nombres de club de cada fuente y el oficial |
| `models/staging/<sistema>/` | Fuentes de bronze (sources + freshness) y una vista por tabla: renombrar y castear |
| `models/silver/<sistema>/` | Modelo entidad-relación normalizado (16 tablas), con sus tests y documentación |
| `macros/` | `limpiar_fecha` y `normalizar_nombre` |
| `tests/singular/` | Test de negocio: los goles de los jugadores cuadran con el marcador |
| `dbt_project.yml`, `packages.yml` | Configuración del proyecto dbt y paquetes (dbt_utils) |
| `docs/` | Documentación técnica de cada capa |

## Estado

| Fase | Estado |
|------|--------|
| Caso de uso y dataset | ✅ |
| Snowflake: entorno, carga de bronze y clones PRE/PRO | ✅ |
| dbt: conexión, variables de entorno, sources y freshness | ✅ |
| Seeds | ✅ |
| Staging (renombrar y castear) | ✅ |
| Silver (modelo entidad-relación, 16 tablas, una incremental) | ✅ |
| Calidad: 119 tests, documentación y macros | ✅ |
| Gold (modelo dimensional + Cortex AI) | ⬜ |
| Power BI | ⬜ |

Documentación técnica:
- Configuración de Snowflake y dbt: [`docs/00_configuracion_dbt_snowflake.md`](docs/00_configuracion_dbt_snowflake.md)
- Capa bronze (tablas, decisiones y problemas de calidad): [`docs/01_bronze.md`](docs/01_bronze.md)
- Seed y capa staging: [`docs/02_staging.md`](docs/02_staging.md)
- Capa silver (modelo entidad-relación): [`docs/03_silver.md`](docs/03_silver.md)
- Calidad (tests), documentación y macros: [`docs/04_calidad_y_macros.md`](docs/04_calidad_y_macros.md)

## ⚠️ Aviso sobre los datos

Clubes, estadios, árbitros y nombres de jugadores son **reales**, y las plantillas y traspasos se
aproximan a lo que pasó en esas temporadas (pueden tener imprecisiones).
**Todo lo demás es SIMULADO con fines didácticos:** salarios, cláusulas, estadísticas de partido,
resultados, lesiones (salvo tres lesiones largas que fueron públicas), partes médicos, informes de
scouting, fechas de nacimiento exactas, agentes, agencias, médicos y ojeadores. No representan
información real de ninguna persona. Se recomienda mantener el repositorio **privado**.
