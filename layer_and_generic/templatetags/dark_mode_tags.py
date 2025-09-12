from django import template

register = template.Library()

@register.inclusion_tag('LAG/_dark_mode_button.html', takes_context=True)
def dark_mode_button(context):
    """Render the button for toggling dark mode"""
    return {
        'dark_mode': context.get('dark_mode', False)
    }