{# Decide en qué esquema se construye cada modelo:
   - Jobs de DEV, PRE y PRO (target dev/pre/pro): el esquema tal cual  -> rrhh
   - IDE (target default) y jobs de CI: con prefijo personal           -> dbt_jgarcia_rrhh
   Así en desarrollo nadie pisa las tablas de otro, y en PRO los nombres son limpios. #}
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- set invocation_context = env_var('DBT_CLOUD_INVOCATION_CONTEXT', '') -%}

    {%- if custom_schema_name is none -%}
        {{ default_schema }}

    {%- elif invocation_context != 'ci'
         and target.name in ['dev', 'pre', 'pro'] -%}
        {{ custom_schema_name | trim }}

    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}