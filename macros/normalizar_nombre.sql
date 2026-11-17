{# Pasa un nombre a mayúsculas y le quita las tildes, para poder comparar nombres
   que una fuente escribe con tildes ("Brahim Díaz") y otra sin ellas ("Brahim Diaz").
   translate cambia cada letra de la primera lista por la de la misma posición en la segunda. #}
{% macro normalizar_nombre(columna) %}
    translate(
          upper({{ columna }})
        , 'ÀÁÃÉÍÏÑÓÖØÚÜĆČĞŘŠȚ'
        , 'AAAEIINOOOUUCCGRST'
    )
{% endmacro %}