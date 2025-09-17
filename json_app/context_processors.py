def dark_mode_context(request):
    """Inject 'dark_mode' flag into every template context."""
    return {'dark_mode': request.session.get('dark_mode', False)}

def active_app_context(request):
    """Inject active app info and the base template to use.

    Priority:
    1) Session key set by each app when rendering their home/login
    2) URL path prefix
    3) Referer header hint
    4) Default to 'json'
    """
    active_app = request.session.get('active_app')
    if not active_app:
        path = request.path or ''
        if path.startswith('/layer_and_generic/'):
            active_app = 'lag'
        elif path.startswith('/json_app/'):
            active_app = 'json'
        else:
            referer = request.META.get('HTTP_REFERER', '')
            if '/layer_and_generic/' in referer:
                active_app = 'lag'
            elif '/json_app/' in referer:
                active_app = 'json'
            else:
                active_app = 'json'

    active_base_template = 'LAG/base.html' if active_app == 'lag' else 'json_app/base.html'
    return {
        'active_app': active_app,
        'active_base_template': active_base_template,
    }
