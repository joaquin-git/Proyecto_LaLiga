{#
  Los entornos ya están separados por DATABASE (DEV_/PRE_/PRO_LALIGA_SILVER_DB...), así que el
  esquema se usa tal cual: la carpeta silver/rrhh -> esquema RRHH, gold -> LALIGA.
  Si un modelo no define esquema, va al esquema por defecto de la conexión.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim | upper }}
    {%- endif -%}
{%- endmacro %}
