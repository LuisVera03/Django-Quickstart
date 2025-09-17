# Dark mode session-based toggle endpoints.
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def toggle_dark_mode(request):
    """Toggle session flag 'dark_mode' and return JSON (or redirect fallback)."""
    current_dark_mode = request.session.get('dark_mode', False)
    new_dark_mode = not current_dark_mode
    request.session['dark_mode'] = new_dark_mode
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'dark_mode': new_dark_mode, 'status': 'success'})
    return redirect(request.META.get('HTTP_REFERER', '/'))

def get_dark_mode_status(request):
    """Return current session dark mode boolean."""
    return JsonResponse({'dark_mode': request.session.get('dark_mode', False)})
