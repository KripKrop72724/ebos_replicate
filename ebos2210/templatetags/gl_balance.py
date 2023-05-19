from django import template

register = template.Library()

@register.filter(name='handle_negative')
def handle_negative(value):
    """Converts negative value"""
    value = value if value else 0.00
    
    if value < 0:
        value = "(" + "%.2f" % float(str(value).replace("-", "")) + ")"
    else:
        value = "%.2f" % float(value)
        
    return value

@register.filter(name='balance')
def balance(value, index):
    """get value from list"""
           
    return handle_negative(value[index])
