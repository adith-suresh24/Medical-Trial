let currentPage = 0;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadLogs();
    document.getElementById('logSearch')?.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') loadLogs();
    });
});

async function loadLogs() {
    try {
        const params = { skip: currentPage * 20, limit: 20 };
        const search = document.getElementById('logSearch')?.value;
        const action = document.getElementById('logAction')?.value;
        const startDate = document.getElementById('logStartDate')?.value;
        const endDate = document.getElementById('logEndDate')?.value;
        if (search) params.search = search;
        if (action) params.action = action;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const data = await api.getLogs(params);
        const logs = data.logs || [];
        renderLogs(logs);
        renderPagination('logsPagination', data.total || 0, currentPage, 20, (p) => { currentPage = p; loadLogs(); });
    } catch (err) {
        showToast('Failed to load logs: ' + err.message, 'error');
    }
}

function renderLogs(logs) {
    const tbody = document.getElementById('logsTable');
    if (!logs.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding:40px">No logs found</td></tr>';
        return;
    }
    tbody.innerHTML = logs.map(l => `
        <tr>
            <td style="white-space:nowrap">${l.created_at ? new Date(l.created_at).toLocaleString() : 'N/A'}</td>
            <td>${l.username || 'System'}</td>
            <td><span class="badge badge-info">${l.action}</span></td>
            <td>${l.resource || 'N/A'}</td>
            <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${l.details || ''}</td>
            <td>${l.ip_address || 'N/A'}</td>
            <td><span class="badge ${l.status === 'success' ? 'badge-success' : 'badge-danger'}">${l.status || 'success'}</span></td>
        </tr>
    `).join('');
}

function exportLogs() {
    // Simple CSV export
    const table = document.querySelector('#logsTable');
    if (!table || !table.rows.length) { showToast('No logs to export', 'warning'); return; }
    let csv = 'Date/Time,User,Action,Resource,Details,IP,Status\n';
    table.querySelectorAll('tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length) {
            csv += Array.from(cells).map(c => `"${c.textContent.trim()}"`).join(',') + '\n';
        }
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `access_logs_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Logs exported', 'success');
}

function renderPagination(id, total, current, size, cb) {
    const c = document.getElementById(id);
    if (!c) return;
    const pages = Math.ceil(total / size) || 1;
    if (pages <= 1) { c.innerHTML = ''; return; }
    let html = `<button ${current === 0 ? 'disabled' : ''} onclick="logPageClick(${current - 1}, '${id}')">‹</button>`;
    for (let i = 0; i < pages; i++) {
        if (i === 0 || i === pages - 1 || Math.abs(i - current) <= 2)
            html += `<button class="${i === current ? 'active' : ''}" onclick="logPageClick(${i}, '${id}')">${i + 1}</button>`;
        else if (Math.abs(i - current) === 3) html += `<button disabled>...</button>`;
    }
    html += `<button ${current >= pages - 1 ? 'disabled' : ''} onclick="logPageClick(${current + 1}, '${id}')">›</button>`;
    c.innerHTML = html;
}
function logPageClick(page, id) { currentPage = page; loadLogs(); }
