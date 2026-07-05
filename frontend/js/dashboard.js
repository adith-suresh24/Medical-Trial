document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const patients = await api.getPatients({ limit: 1 });
        const reportsData = await api.getReports({ limit: 1 });
        const logsData = await api.getLogs({ limit: 1 });

        // Get more data for stats
        const allPatients = await api.getPatients({ limit: 10000 });
        const totalPatients = allPatients.total || allPatients.length || 0;
        const activePatients = Array.isArray(allPatients)
            ? allPatients.filter(p => p.status === 'active').length
            : (allPatients.patients || []).filter(p => p.status === 'active').length;

        // Update stat cards
        document.getElementById('totalPatients').textContent = totalPatients;
        document.getElementById('activePatients').textContent = activePatients;
        document.getElementById('dischargedPatients').textContent = totalPatients - activePatients;

        // Today's admissions
        const today = new Date().toISOString().split('T')[0];
        const todayAdmissions = Array.isArray(allPatients)
            ? allPatients.filter(p => p.created_at && p.created_at.startsWith(today)).length
            : 0;
        document.getElementById('todayAdmissions').textContent = todayAdmissions;

        // Doctors count
        try {
            const users = await api.getUsers();
            const doctors = users.filter(u => u.role === 'doctor').length;
            document.getElementById('totalDoctors').textContent = doctors;
        } catch (e) {
            document.getElementById('totalDoctors').textContent = '0';
        }

        // Pending reports
        const allReports = await api.getReports({ limit: 10000 });
        const pendingReports = Array.isArray(allReports)
            ? allReports.filter(r => r.is_finalized === 0).length
            : 0;
        document.getElementById('pendingReports').textContent = pendingReports;

    } catch (err) {
        showToast('Failed to load dashboard stats: ' + err.message, 'error');
    }
}
