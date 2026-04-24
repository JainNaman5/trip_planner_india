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
});
