def dark_mode_context(request):
    """Inject 'dark_mode' flag into every template context."""
    return {'dark_mode': request.session.get('dark_mode', False)}
