# Moneyball LaLiga ⚽ — eficiencia salarial de las plantillas

Proyecto de Data Engineering (formación Cívica) con **Snowflake + dbt + Cortex AI + Power BI**
sobre la liga española de fútbol masculino, temporadas **2024/25 y 2025/26**.

## El caso de uso (en una frase)

> **"¿Qué jugadores rinden más por cada euro que cobran, cuánto dinero perdemos con los lesionados
> y a quién deberíamos fichar?"**

**Cliente:** la Dirección Deportiva de un club de LaLiga.
**Por qué es un problema de negocio real:** LaLiga fija a cada club un *límite de coste de plantilla
deportiva*. Cada euro de salario mal invertido (un jugador caro que no juega, o que se pasa media
temporada en la enfermería) es un euro que no se puede usar para fichar. El director deportivo
necesita datos, no intuición, para decidir a quién renovar, vender o fichar.

### Preguntas de negocio que el modelo debe responder

| # | Pregunta | Ejemplo de respuesta |
|---|----------|----------------------|
| P1 | ¿Cuánto nos cuesta cada minuto jugado, cada gol y cada asistencia de cada jugador? ¿Quién rinde por encima / por debajo de lo que cobra? | "El jugador X cuesta 410 € por minuto; el jugador Y, 35 €" |
| P2 | ¿Cuánto salario pagamos a jugadores lesionados (coste de enfermería) por club, tipo de lesión y mes? | "Este club pagó 6,2 M€ a lesionados en 2024/25; el 40 % por roturas fibrilares" |
| P3 | ¿Qué jugadores recomiendan fichar los ojeadores y qué encaje económico tienen? | IA (Cortex) clasifica 1.000+ informes en *Fichar / Seguir / Descartar* y resume cada jugador |

## Arquitectura (medallion)

```
FUENTES (6 CSV)          BRONZE (DEV_LALIGA_BRONZE_DB)      SILVER ({ENV}_LALIGA_SILVER_DB)       GOLD ({ENV}_LALIGA_GOLD_DB)      CONSUMO
API partidos      ─┐                                 modelo entidad-relación         modelo dimensional              Power BI
Proveedor stats   ─┤     copia fiel, todo VARCHAR    limpieza + normalización        hechos + dimensiones            (Copilot)
RRHH contratos    ─┼──►  + metadatos de carga   ──►  claves PK/FK, tipos         ──► Cortex: AI_CLASSIFY,       ──►
Mercado/traspasos ─┤     (COPY INTO)                 (dbt)                            AI_FILTER, AI_COMPLETE (dbt)
Servicio médico   ─┤
App scouting      ─┘
```

## Estructura del repositorio

| Carpeta | Contenido |
|---------|-----------|
| `data/bronze/` | Los 6 CSV de origen (generados) |
| `data/validacion/` | "Verdad" oculta para medir la precisión de AI_CLASSIFY / AI_FILTER (no se carga en bronze) |
| `scripts/` | Generador del dataset (`generar_bronze.py`) y datos maestros |
| `snowflake/` | `01_entorno_laliga.sql` (warehouse, databases y roles) y `02_bronze_laliga.sql` (carga de bronze) |
| `models/silver`, `models/gold` | Modelos dbt (se irán creando paso a paso) |
| `docs/` | Documentación de cada paso: caso de uso, bronze, modelado silver, modelado gold |

## Paso a paso

1. ✅ Caso de uso y preguntas de negocio
2. ✅ **Bronze**: dataset + carga en Snowflake → [`docs/01_bronze.md`](docs/01_bronze.md)
3. ⬜ **Silver**: modelo conceptual → lógico (DBML) → registro de decisiones → físico (dbt)
4. ⬜ **Gold**: grano, medidas, dimensiones + Cortex AI
5. ⬜ **Power BI**

Configuración de dbt Cloud + Snowflake (convención del curso: `WH_LALIGA`, `{ENV}_LALIGA_BRONZE/SILVER/GOLD_DB`, `{ENV}_LALIGA_TRANSFORM_ROLE`): [`docs/00_configuracion_dbt_snowflake.md`](docs/00_configuracion_dbt_snowflake.md)

## ⚠️ Aviso sobre los datos

Clubes, estadios, árbitros y nombres de jugadores son **reales**, y las plantillas y traspasos se
aproximan a lo que pasó en esas temporadas (pueden tener imprecisiones).
**Todo lo demás es SIMULADO con fines didácticos:** salarios, cláusulas, estadísticas de partido,
resultados, lesiones (salvo tres lesiones largas que fueron públicas), partes médicos, informes de
scouting, fechas de nacimiento exactas, agentes, agencias, médicos y ojeadores. No representan
información real de ninguna persona. Se recomienda mantener el repositorio **privado**.
