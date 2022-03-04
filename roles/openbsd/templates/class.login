{{ item.key }}:\
{% for key, value in item.value | dictsort %}
	:{{ key }}={{ value }}:{% if not loop.last %}\{% endif %}

{% endfor %}
