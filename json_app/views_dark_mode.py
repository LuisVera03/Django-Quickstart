from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def toggle_dark_mode(request):
    """
    View to toggle between light and dark mode
    Stores user preference in session
    """
    # Get current dark mode state from session
    current_dark_mode = request.session.get('dark_mode', False)
    
    # Toggle the state
    new_dark_mode = not current_dark_mode
    
    # Save new state in session
    request.session['dark_mode'] = new_dark_mode
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'dark_mode': new_dark_mode,
            'status': 'success'
        })
    
    # If not AJAX, redirect to previous page
    return redirect(request.META.get('HTTP_REFERER', '/'))

def get_dark_mode_status(request):
    """
    View to get current dark mode status
    """
    dark_mode = request.session.get('dark_mode', False)
    return JsonResponse({'dark_mode': dark_mode})
