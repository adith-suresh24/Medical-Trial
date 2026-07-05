let dbPage = 0;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadDiagnosisDB();
    document.getElementById('searchDB')?.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') loadDiagnosisDB();
    });
});

async function loadDiagnosisDB() {
    try {
        const search = document.getElementById('searchDB')?.value || '';
        const severity = document.getElementById('severityFilter')?.value || '';
        const params = { skip: dbPage * 10, limit: 10 };
        if (search) params.search = search;
        if (severity) params.severity = severity;
        const data = await api.getDiagnosisDatabase(params);
        const conditions = data.conditions || [];
        renderDB(conditions);
        renderPagination('dbPagination', data.total || 0, dbPage, 10, (p) => { dbPage = p; loadDiagnosisDB(); });
    } catch (err) {
        showToast('Failed to load database: ' + err.message, 'error');
    }
}

function renderDB(conditions) {
    const tbody = document.getElementById('dbTable');
    if (!conditions.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding:40px">No conditions found</td></tr>';
        return;
    }
    tbody.innerHTML = conditions.map(c => `
        <tr>
            <td><strong>${c.condition_name}</strong></td>
            <td>${c.icd_code || 'N/A'}</td>
            <td><span class="badge ${c.severity === 'critical' ? 'badge-danger' : c.severity === 'high' ? 'badge-warning' : c.severity === 'moderate' ? 'badge-info' : 'badge-success'}">${c.severity}</span></td>
            <td>${(c.symptoms || '').substring(0, 60)}...</td>
            <td><button class="btn btn-sm btn-primary" onclick="viewCondition(${c.id})">View</button></td>
        </tr>
    `).join('');
}

async function viewCondition(id) {
    try {
        const data = await api.getDiagnosisDatabase({ search: '', limit: 1000 });
        const conditions = data.conditions || [];
        const c = conditions.find(x => x.id === id);
        if (!c) { showToast('Condition not found', 'error'); return; }
        document.getElementById('conditionModalTitle').textContent = c.condition_name;
        document.getElementById('conditionDetailContent').innerHTML = `
            <div class="grid-2">
                <div class="form-group"><label>ICD Code</label><p><strong>${c.icd_code || 'N/A'}</strong></p></div>
                <div class="form-group"><label>Severity</label><p><span class="badge ${c.severity === 'critical' ? 'badge-danger' : c.severity === 'high' ? 'badge-warning' : c.severity === 'moderate' ? 'badge-info' : 'badge-success'}">${c.severity}</span></p></div>
            </div>
            <div class="form-group"><label>Description</label><p>${c.description || 'N/A'}</p></div>
            <div class="form-group"><label>Symptoms</label><p>${c.symptoms || 'N/A'}</p></div>
            <div class="form-group"><label>Recommendations</label><p>${c.recommendations || 'N/A'}</p></div>
            <div class="form-group"><label>Common Treatments</label><p>${c.common_treatments || 'N/A'}</p></div>
        `;
        document.getElementById('conditionModal').classList.add('active');
    } catch (err) {
        showToast('Failed to load condition: ' + err.message, 'error');
    }
}

async function matchSymptoms() {
    const symptoms = document.getElementById('symptomInput').value.trim();
    if (!symptoms) { showToast('Please enter symptoms', 'warning'); return; }
    const resultsDiv = document.getElementById('matchResults');
    resultsDiv.innerHTML = '<div class="text-center" style="padding:20px"><div class="spinner" style="margin:0 auto"></div><p class="mt-1">Matching symptoms...</p></div>';
    try {
        const data = await api.matchSymptoms({ symptoms });
        const matches = data.matches || [];
        if (!matches.length) {
            resultsDiv.innerHTML = '<p class="text-center" style="padding:20px;color:var(--gray-500)">No matching conditions found</p>';
            return;
        }
        resultsDiv.innerHTML = `<h3 class="mb-2">${data.total_matches} Matches Found</h3>
            ${matches.map(m => `<div class="card mb-2" style="border-left:4px solid ${m.match_percentage > 70 ? 'var(--danger)' : m.match_percentage > 50 ? 'var(--warning)' : 'var(--info)'}">
                <div class="flex-between">
                    <h4>${m.condition_name}</h4>
                    <span class="badge ${m.severity === 'critical' ? 'badge-danger' : m.severity === 'high' ? 'badge-warning' : 'badge-info'}">${m.severity}</span>
                </div>
                <p style="color:var(--gray-500);font-size:13px">Match: ${m.match_percentage}% | ICD: ${m.icd_code || 'N/A'}</p>
                <p style="font-size:13px;margin-top:8px"><strong>Matched symptoms:</strong> ${m.matched_symptoms.join(', ')}</p>
                <p style="font-size:13px"><strong>Recommendations:</strong> ${m.recommendations || 'N/A'}</p>
                <p style="font-size:11px;color:var(--gray-500);margin-top:4px"><em>This is AI-assisted analysis. Final diagnosis is the doctor's responsibility.</em></p>
            </div>`).join('')}`;
    } catch (err) {
        resultsDiv.innerHTML = `<p style="color:var(--danger)">Failed: ${err.message}</p>`;
    }
}

function closeModal(id) { document.getElementById(id).classList.remove('active'); }
function renderPagination(id, total, current, size, cb) {
    const c = document.getElementById(id);
    if (!c) return;
    const pages = Math.ceil(total / size) || 1;
    if (pages <= 1) { c.innerHTML = ''; return; }
    let html = `<button ${current === 0 ? 'disabled' : ''} onclick="dbPageClick(${current - 1}, '${id}')">‹</button>`;
    for (let i = 0; i < pages; i++) {
        if (i === 0 || i === pages - 1 || Math.abs(i - current) <= 2)
            html += `<button class="${i === current ? 'active' : ''}" onclick="dbPageClick(${i}, '${id}')">${i + 1}</button>`;
        else if (Math.abs(i - current) === 3) html += `<button disabled>...</button>`;
    }
    html += `<button ${current >= pages - 1 ? 'disabled' : ''} onclick="dbPageClick(${current + 1}, '${id}')">›</button>`;
    c.innerHTML = html;
}
function dbPageClick(page, id) { dbPage = page; loadDiagnosisDB(); }
