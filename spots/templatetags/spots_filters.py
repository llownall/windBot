from typing import List

from django import template

from spots.models import WindDirection

register = template.Library()


@register.filter
def to_wind_directions(directions: List[int]):
    directions_labels = [str(WindDirection(code).label) for code in directions]
    return ', '.join(directions_labels)
