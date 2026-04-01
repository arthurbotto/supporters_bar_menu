function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.querySelector('.theme-toggle').textContent = isDark ? '☀' : '☾';
}

document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);

if (localStorage.getItem('theme') === 'dark') {
    document.querySelector('.theme-toggle').textContent = '☀';
}