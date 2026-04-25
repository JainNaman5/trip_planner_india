// main.js — Trip Planner India frontend logic
document.addEventListener('DOMContentLoaded', () => {
    // Scroll effect on top bar
    const topBar = document.getElementById('topBar');
    if (topBar) {
        window.addEventListener('scroll', () => {
            topBar.style.boxShadow = window.scrollY > 10
                ? '0 4px 20px rgba(143,78,0,.1)'
                : '0 1px 3px rgba(143,78,0,.05)';
        });
    }

    // === Dark Mode Toggle ===
    const toggle = document.getElementById('themeToggle');
    const icon = document.getElementById('themeIcon');
    const body = document.body;

    // Load saved preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        if (icon) icon.textContent = 'light_mode';
    }

    if (toggle) {
        toggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            if (icon) icon.textContent = isDark ? 'light_mode' : 'dark_mode';
        });
    }
});
