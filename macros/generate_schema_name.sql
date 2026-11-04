{#
  Dev  (target.name != 'prod'): todo en el esquema personal del desarrollador (p. ej. DBT_JOAQUIN).
  Prod (target.name == 'prod'): cada carpeta en su esquema -> SILVER y GOLD.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if target.name == 'prod' and custom_schema_name is not none -%}
        {{ custom_schema_name | trim | upper }}
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
