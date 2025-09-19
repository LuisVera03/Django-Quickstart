const DARK_MODE_TOGGLE_URL = '/toggle_dark_mode/';
const DARK_MODE_STATUS_URL = '/dark_mode_status/';

// Function to toggle dark mode
function toggleDarkMode() {
    fetch(DARK_MODE_TOGGLE_URL, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                applyDarkMode(data.dark_mode);
                updateToggleButton(data.dark_mode);
            }
        })
        .catch(err => console.error('Error toggling dark mode:', err));
}

// Function to apply dark mode
function applyDarkMode(isDark) {
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    try {
        localStorage.setItem('dark_mode_pref', isDark ? 'true' : 'false');
    } catch(e) {}
}

// Function to update toggle button text
function updateToggleButton(isDark) {
    const button = document.getElementById('darkModeToggle');
    if (button) {
        const newLabel = isDark ? 'Light' : 'Dark';
        if (button.textContent !== newLabel) {
            button.textContent = newLabel;
        }
        button.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
        button.setAttribute('aria-pressed', isDark ? 'true' : 'false');
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
    // If the dark mode is actived do not reapply
    const root = document.documentElement;
    const hadThemeAttribute = root.hasAttribute('data-theme');
    fetch(DARK_MODE_STATUS_URL)
        .then(r => r.json())
        .then(data => {
            let serverDark = !!data.dark_mode;
            // If inline applied dark and server matches, just update button
            if (hadThemeAttribute && serverDark === true) {
                updateToggleButton(true);
                return;
            }
            // If inline did not apply dark and server says dark -> apply
            if (!hadThemeAttribute && serverDark) {
                applyDarkMode(true);
                updateToggleButton(true);
                return;
            }
            // If both say light, sync storage and button
            if (!serverDark) {
                try { localStorage.setItem('dark_mode_pref','false'); } catch(e) {}
                updateToggleButton(false);
            }
        })
        .catch(err => {
            // Just log; we do not overwrite what was already decided inline
            console.warn('Dark mode status fetch failed:', err);
            updateToggleButton(root.hasAttribute('data-theme'));
        });
});
