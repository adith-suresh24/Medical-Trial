let currentPage = 0;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadReports();
    loadPatientSelect();
    document.getElementById('searchReport')?.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') loadReports();
    });
    // Check if we should open new report for a specific patient
    const patientId = new URLSearchParams(window.location.search).get('patient_id');
    if (patientId) {
        setTimeout(() => openNewReport(patientId), 500);
    }
});

async function loadReports() {
    try {
        const search = document.getElementById('searchReport')?.value || '';
        const params = { skip: currentPage * 10, limit: 10 };
        if (search) params.search = search;
        const data = await api.getReports(params);
        const reports = data.reports || [];
        const total = data.total || 0;
        renderReports(reports);
        renderPagination('reportsPagination', total, currentPage, 10, (p) => { currentPage = p; loadReports(); });
    } catch (err) {
        showToast('Failed to load reports: ' + err.message, 'error');
    }
}

function renderReports(reports) {
    const tbody = document.getElementById('reportsTable');
    if (!reports.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding:40px">No reports found</td></tr>';
        return;
    }
    tbody.innerHTML = reports.map(r => `
        <tr>
            <td>${new Date(r.created_at).toLocaleDateString()}</td>
            <td><a href="patient-detail.html?id=${r.patient_id}">Patient #${r.patient_id}</a></td>
            <td>${(r.symptoms || '').substring(0, 40)}...</td>
            <td>${r.diagnosis || 'Pending'}</td>
            <td>Dr. #${r.doctor_id}</td>
            <td><span class="badge ${r.is_finalized ? 'badge-success' : 'badge-warning'}">${r.is_finalized ? 'Finalized' : 'Draft'}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editReport(${r.id})">Edit</button>
                <button class="btn btn-sm btn-info" onclick="viewAISummary(${r.id})">🤖 AI</button>
                <button class="btn btn-sm btn-danger" onclick="deleteReport(${r.id})">Del</button>
            </td>
        </tr>
    `).join('');
}

async function loadPatientSelect() {
    try {
        const data = await api.getPatients({ limit: 10000 });
        const patients = data.patients || [];
        const select = document.getElementById('reportPatientId');
        patients.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.patient_id} - ${p.first_name} ${p.last_name}`;
            select.appendChild(opt);
        });
    } catch (err) { /* ignore */ }
}

function openNewReport(patientId) {
    document.getElementById('reportModalTitle').textContent = 'New Medical Report';
    document.getElementById('reportForm').reset();
    document.getElementById('editReportId').value = '';
    if (patientId) document.getElementById('reportPatientId').value = patientId;
    document.getElementById('reportModal').classList.add('active');
}

async function editReport(id) {
    try {
        const report = await api.getReport(id);
        document.getElementById('reportModalTitle').textContent = 'Edit Report';
        document.getElementById('editReportId').value = report.id;
        document.getElementById('reportPatientId').value = report.patient_id;
        document.getElementById('symptoms').value = report.symptoms;
        document.getElementById('observations').value = report.observations || '';
        document.getElementById('doctorNotes').value = report.doctor_notes || '';
        document.getElementById('diagnosis').value = report.diagnosis || '';
        document.getElementById('treatment').value = report.treatment || '';
        document.getElementById('medications').value = report.prescribed_medications || '';
        document.getElementById('followUpDate').value = report.follow_up_date ? report.follow_up_date.replace(' ', 'T') : '';
        document.getElementById('reportModal').classList.add('active');
    } catch (err) {
        showToast('Failed to load report: ' + err.message, 'error');
    }
}

async function saveReport() {
    const data = {
        patient_id: parseInt(document.getElementById('reportPatientId').value),
        symptoms: document.getElementById('symptoms').value,
        observations: document.getElementById('observations').value || null,
        doctor_notes: document.getElementById('doctorNotes').value || null,
        diagnosis: document.getElementById('diagnosis').value || null,
        treatment: document.getElementById('treatment').value || null,
        prescribed_medications: document.getElementById('medications').value || null,
        follow_up_date: document.getElementById('followUpDate').value ? new Date(document.getElementById('followUpDate').value).toISOString() : null,
    };
    try {
        const editId = document.getElementById('editReportId').value;
        if (editId) {
            await api.updateReport(editId, data);
            showToast('Report updated', 'success');
        } else {
            await api.createReport(data);
            showToast('Report created', 'success');
        }
        closeModal('reportModal');
        loadReports();
    } catch (err) {
        showToast('Failed to save report: ' + err.message, 'error');
    }
}

async function deleteReport(id) {
    if (!confirm('Delete this report?')) return;
    try {
        await api.deleteReport(id);
        showToast('Report deleted', 'success');
        loadReports();
    } catch (err) {
        showToast('Delete failed: ' + err.message, 'error');
    }
}

async function generateAISummary() {
    const editId = document.getElementById('editReportId').value;
    if (!editId) {
        showToast('Save the report first before generating AI summary', 'warning');
        return;
    }
    document.getElementById('aiSummaryModal').classList.add('active');
    document.getElementById('aiSummaryContent').innerHTML = `
        <div class="text-center" style="padding:40px">
            <div class="spinner" style="margin:0 auto"></div>
            <p class="mt-2">🤖 AI analyzing patient data...</p>
        </div>`;
    try {
        const result = await api.generateAISummary(editId);
        document.getElementById('aiSummaryContent').innerHTML = `
            <div style="margin-bottom:16px">
                <span class="badge ${result.risk_level === 'low' ? 'badge-success' : result.risk_level === 'moderate' ? 'badge-warning' : 'badge-danger'}">
                    Risk Level: ${result.risk_level}
                </span>
                <small style="color:var(--gray-500);margin-left:8px">${result.processing_time_ms}ms</small>
            </div>
            <div class="form-group"><label>AI Summary</label><p style="background:var(--gray-100);padding:12px;border-radius:var(--radius)">${result.summary || 'N/A'}</p></div>
            <div class="form-group"><label>Recommendations</label><p style="background:var(--gray-100);padding:12px;border-radius:var(--radius)">${result.recommendations || 'N/A'}</p></div>
            <div class="form-group"><label>Possible Conditions</label><p style="background:var(--gray-100);padding:12px;border-radius:var(--radius)">${result.possible_conditions || 'N/A'}</p></div>
            <p style="font-size:11px;color:var(--gray-500);margin-top:12px"><em>${result.disclaimer || 'AI-assisted analysis for reference only'}</em></p>
        `;
    } catch (err) {
        document.getElementById('aiSummaryContent').innerHTML = `<p class="text-center" style="color:var(--danger)">Failed: ${err.message}</p>`;
    }
}

async function viewAISummary(reportId) {
    try {
        await generateAISummary();
    } catch (err) {
        // generateAISummary handles the UI
    }
}

function closeModal(id) { document.getElementById(id).classList.remove('active'); }
function renderPagination(id, total, current, size, cb) {
    const c = document.getElementById(id);
    if (!c) return;
    const pages = Math.ceil(total / size) || 1;
    if (pages <= 1) { c.innerHTML = ''; return; }
    let html = `<button ${current === 0 ? 'disabled' : ''} onclick="pageClick(${current - 1}, '${id}')">‹</button>`;
    for (let i = 0; i < pages; i++) {
        if (i === 0 || i === pages - 1 || Math.abs(i - current) <= 2)
            html += `<button class="${i === current ? 'active' : ''}" onclick="pageClick(${i}, '${id}')">${i + 1}</button>`;
        else if (Math.abs(i - current) === 3) html += `<button disabled>...</button>`;
    }
    html += `<button ${current >= pages - 1 ? 'disabled' : ''} onclick="pageClick(${current + 1}, '${id}')">›</button>`;
    c.innerHTML = html;
}
function pageClick(page, id) { currentPage = page; loadReports(); }
