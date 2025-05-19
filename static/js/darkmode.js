/**
 * GlaCK0N GarageHub - Dark Mode Toggle
 * This file handles dark mode functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDarkMode();
});

/**
 * Initialize dark mode functionality
 */
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (!darkModeToggle) return;
    
    // Set initial mode based on localStorage or system preference
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode) {
        // Use saved preference if available
        setTheme(savedMode === 'dark' ? 'dark' : 'light');
    } else {
        // Otherwise check system preference
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDarkMode ? 'dark' : 'light');
    }
    
    // Add click event to toggle
    darkModeToggle.addEventListener('click', function() {
        // Toggle between light and dark theme
        const currentTheme = document.body.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        setTheme(newTheme);
        
        // Save preference to localStorage
        localStorage.setItem('darkMode', newTheme);
    });
    
    // Also listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        // Only change if the user hasn't set a preference
        if (!localStorage.getItem('darkMode')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

/**
 * Set the theme for the application
 * @param {string} theme - 'light' or 'dark'
 */
function setTheme(theme) {
    document.body.setAttribute('data-bs-theme', theme);
    
    // Update toggle button icon
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        const icon = darkModeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
    
    // Set theme color meta tag for browser UI
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.setAttribute('content', theme === 'dark' ? '#121212' : '#ffffff');
    }
}
