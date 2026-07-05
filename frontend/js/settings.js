document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadProfile();
    document.getElementById('passwordForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await changePassword();
    });
});

function loadProfile() {
    const user = api.getUser();
    if (!user) return;
    document.getElementById('profileName').textContent = user.full_name;
    document.getElementById('profileUsername').textContent = user.username;
    document.getElementById('profileEmail').textContent = user.email;
    document.getElementById('profileRole').textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
}

async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    try {
        await api.changePassword({ current_password: currentPassword, new_password: newPassword });
        showToast('Password changed successfully', 'success');
        document.getElementById('passwordForm').reset();
    } catch (err) {
        showToast('Failed: ' + err.message, 'error');
    }
}
