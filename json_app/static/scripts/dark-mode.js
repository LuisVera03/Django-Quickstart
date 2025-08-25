// Function to toggle dark mode
function toggleDarkMode() {
    fetch('/json_app/toggle_dark_mode/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            applyDarkMode(data.dark_mode);
            updateToggleButton(data.dark_mode);
        }
    })
    .catch(error => {
        console.error('Error toggling dark mode:', error);
    });
}

// Function to apply dark mode
function applyDarkMode(isDark) {
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
}

// Function to update toggle button text
function updateToggleButton(isDark) {
    const button = document.getElementById('darkModeToggle');
    if (button) {
        button.textContent = isDark ? 'Light' : 'Dark';
        button.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
    }
}

// Function to get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get current dark mode status
    fetch('/json_app/dark_mode_status/')
        .then(response => response.json())
        .then(data => {
            applyDarkMode(data.dark_mode);
            updateToggleButton(data.dark_mode);
        })
        .catch(error => {
            console.error('Error getting dark mode status:', error);
        });
});
