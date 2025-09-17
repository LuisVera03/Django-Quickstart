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
    if (!button) return;
    const lightIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 17q-2.075 0-3.537-1.463T7 12t1.463-3.537T12 7t3.538 1.463T17 12t-1.463 3.538T12 17m-7-4H1v-2h4zm18 0h-4v-2h4zM11 5V1h2v4zm0 18v-4h2v4zM6.4 7.75L3.875 5.325L5.3 3.85l2.4 2.5zm12.3 12.4l-2.425-2.525L17.6 16.25l2.525 2.425zM16.25 6.4l2.425-2.525L20.15 5.3l-2.5 2.4zM3.85 18.7l2.525-2.425L7.75 17.6l-2.425 2.525z"/></svg>';
    const darkIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M12 21q-3.75 0-6.375-2.625T3 12t2.625-6.375T12 3q.35 0 .688.025t.662.075q-1.025.725-1.638 1.888T11.1 7.5q0 2.25 1.575 3.825T16.5 12.9q1.375 0 2.525-.613T20.9 10.65q.05.325.075.662T21 12q0 3.75-2.625 6.375T12 21"/></svg>';
    // When isDark is true, we show light icon
    const desired = isDark ? lightIcon : darkIcon;
    if (button.innerHTML.trim() !== desired) {
        button.innerHTML = desired;
    }
    button.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
    button.setAttribute('aria-pressed', isDark ? 'true' : 'false');
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