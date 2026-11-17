{# Convierte un texto en fecha aceptando los dos formatos que llegan de origen:
   'YYYY-MM-DD' y 'DD/MM/YYYY'. Si no es ninguno de los dos, devuelve NULL. #}
{% macro limpiar_fecha(columna) %}
    coalesce(
          try_to_date({{ columna }}, 'YYYY-MM-DD')
        , try_to_date({{ columna }}, 'DD/MM/YYYY')
    )
{% endmacro %}