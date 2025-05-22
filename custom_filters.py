#from django import template

#register = template.Library()

#@register.filter
#def multiply(value, arg):
 #   """Multiply the value by the arg."""
  #  return value * arg

from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_total(items):
    """Calculate total for an order's items"""
    return sum(item[3] * item[4] for item in items)  # quantity * price 
@register.filter
def sum_subtotals(items):
    """Safely sum subtotals with None/empty handling"""
    if not items:  # Handles None or empty list
        return Decimal('0.00')
    
    try:
        return sum(Decimal(str(item[3])) * Decimal(str(item[4])) for item in items if len(item) > 4)
    except:
        return Decimal('0.00')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)