// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) {
        const div = document.createElement('div');
        div.id = 'toastContainer';
        div.className = 'toast-container';
        document.body.appendChild(div);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.getElementById('toastContainer').appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// Toggle password visibility
function togglePassword() {
    const pwd = document.getElementById('password');
    pwd.type = pwd.type === 'password' ? 'text' : 'password';
}

// Login form handler
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) return;

    // Redirect if already logged in
    if (api.getToken()) {
        window.location.href = 'dashboard.html';
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('authError');
        const btn = document.getElementById('loginBtn');

        btn.disabled = true;
        btn.textContent = 'Signing in...';
        errorEl.classList.remove('show');

        try {
            const result = await api.login(username, password);
            api.setToken(result.access_token);
            api.setUser(result.user);
            window.location.href = 'dashboard.html';
        } catch (err) {
            errorEl.textContent = err.message;
            errorEl.classList.add('show');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    });
});

// Logout function
async function logout() {
    try {
        await api.logout();
    } catch (e) {
        // ignore
    }
    api.removeToken();
    api.removeUser();
    window.location.href = 'login.html';
}

// Check auth on page load (for dashboard pages)
function checkAuth() {
    const token = api.getToken();
    if (!token) {
        window.location.href = 'login.html';
        return null;
    }
    const user = api.getUser();
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    return user;
}

// Initialize dashboard components
function initDashboard() {
    const user = checkAuth();
    if (!user) return;

    // Set user info in header
    const userAvatar = document.querySelector('.user-avatar');
    const userName = document.querySelector('.user-info strong');
    const userRole = document.querySelector('.user-info small');

    if (userAvatar) {
        const initials = user.full_name.split(' ').map(n => n[0]).join('').toUpperCase();
        userAvatar.textContent = initials;
    }
    if (userName) userName.textContent = user.full_name;
    if (userRole) userRole.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);

    // Highlight active nav
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && href.includes(currentPage)) {
            item.classList.add('active');
        }
    });

    // Mobile sidebar toggle
    const hamburger = document.querySelector('.hamburger');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }
}
