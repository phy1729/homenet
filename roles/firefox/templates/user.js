{% for key, value in preferences | dictsort %}
{% if (value | type_debug) in ('list', 'dict') %}
{% set value=(value | tojson) %}
{% endif %}
user_pref("{{ key }}", {{ value | tojson }});
{% endfor %}
