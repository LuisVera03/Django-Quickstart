def dark_mode_context(request):
    """
    Context processor to make dark mode state available
    in all templates
    """
    return {
        'dark_mode': request.session.get('dark_mode', False)
    }
