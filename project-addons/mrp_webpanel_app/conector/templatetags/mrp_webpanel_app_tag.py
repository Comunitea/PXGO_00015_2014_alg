
from datetime import datetime
from django import template
register = template.Library()

@register.filter
def traduccion(arg):
    estados = {'draft': 'Borrador', 'open': 'Abierto', 'confirmed': 'Confirmada', 'assigned': 'Lista para producir', 'ready': 'Listo para fabricar', 'in_production': 'Produccion iniciada',}
    return estados.get(arg)


@register.filter
def parse_date(date_string, format):
    """
    Return a datetime corresponding to date_string, parsed according to format.

    For example, to re-display a date string in another format::

        {{ "01/01/1970"|parse_date:"%m/%d/%Y"|date:"F jS, Y" }}

    """
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None
