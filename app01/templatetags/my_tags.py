from django import template
register = template.Library()


@register.filter
def get_error(error_dict):
    return error_dict.get('__all__')


