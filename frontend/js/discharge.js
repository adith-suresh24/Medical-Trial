let currentPage = 0;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadDischarges();
    loadPatientSelect();
});

async function loadDischarges() {
    try {
        const data = await api.getDischargeReports({ skip: currentPage * 10, limit: 10 });
        const reports = data.reports || [];
        renderDischarges(reports);
        renderPagination('dischargePagination', data.total || 0, currentPage, 10, (p) => { currentPage = p; loadDischarges(); });
    } catch (err) {
        showToast('Failed to load discharges: ' + err.message, 'error');
    }
}

function renderDischarges(reports) {
    const tbody = document.getElementById('dischargeTable');
    if (!reports.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding:40px">No discharge reports found</td></tr>';
        return;
    }
    tbody.innerHTML = reports.map(r => `
        <tr>
            <td>${new Date(r.created_at).toLocaleDateString()}</td>
            <td><a href="patient-detail.html?id=${r.patient_id}">Patient #${r.patient_id}</a></td>
            <td>${(r.diagnosis || '').substring(0, 50)}...</td>
            <td>${r.discharge_date}</td>
            <td>${r.pdf_path ? '<span class="badge badge-success">✅ Generated</span>' : '<span class="badge badge-secondary">❌ Not generated</span>'}</td>
            <td>
                ${r.pdf_path ? `<a href="${api.getDischargePDF(r.id)}" class="btn btn-sm btn-success" download>📄 PDF</a>` : ''}
                <button class="btn btn-sm btn-primary" onclick="generatePDF(${r.id})">🔄 Generate PDF</button>
            </td>
        </tr>
    `).join('');
}

async function loadPatientSelect() {
    try {
        const data = await api.getPatients({ limit: 10000 });
        const patients = data.patients || [];
        const select = document.getElementById('dischargePatientId');
        patients.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.patient_id} - ${p.first_name} ${p.last_name}`;
            select.appendChild(opt);
        });
    } catch (err) { /* ignore */ }
}

async function saveDischarge() {
    const data = {
        patient_id: parseInt(document.getElementById('dischargePatientId').value),
        diagnosis: document.getElementById('dischargeDiagnosis').value,
        treatment_summary: document.getElementById('dischargeTreatment').value,
        medications_prescribed: document.getElementById('dischargeMeds').value || null,
        follow_up_instructions: document.getElementById('dischargeInstructions').value || null,
        dietary_recommendations: document.getElementById('dischargeDiet').value || null,
        activity_restrictions: document.getElementById('dischargeActivity').value || null,
        additional_notes: document.getElementById('dischargeNotes').value || null,
        discharge_date: document.getElementById('dischargeDate').value,
        follow_up_date: document.getElementById('dischargeFollowUp').value || null,
    };
    try {
        const report = await api.createDischargeReport(data);
        await api.generateDischargePDF(report.id);
        showToast('Discharge report created and PDF generated', 'success');
        closeModal('dischargeModal');
        loadDischarges();
    } catch (err) {
        showToast('Failed: ' + err.message, 'error');
    }
}

async function generatePDF(id) {
    try {
        await api.generateDischargePDF(id);
        showToast('PDF generated successfully', 'success');
        loadDischarges();
    } catch (err) {
        showToast('PDF generation failed: ' + err.message, 'error');
    }
}

function openNewDischarge() {
    document.getElementById('dischargeForm').reset();
    document.getElementById('dischargeDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('dischargeModal').classList.add('active');
}

function closeModal(id) { document.getElementById(id).classList.remove('active'); }
function renderPagination(id, total, current, size, cb) {
    const c = document.getElementById(id);
    if (!c) return;
    const pages = Math.ceil(total / size) || 1;
    if (pages <= 1) { c.innerHTML = ''; return; }
    let html = `<button ${current === 0 ? 'disabled' : ''} onclick="dcPageClick(${current - 1}, '${id}')">‹</button>`;
    for (let i = 0; i < pages; i++) {
        if (i === 0 || i === pages - 1 || Math.abs(i - current) <= 2)
            html += `<button class="${i === current ? 'active' : ''}" onclick="dcPageClick(${i}, '${id}')">${i + 1}</button>`;
        else if (Math.abs(i - current) === 3) html += `<button disabled>...</button>`;
    }
    html += `<button ${current >= pages - 1 ? 'disabled' : ''} onclick="dcPageClick(${current + 1}, '${id}')">›</button>`;
    c.innerHTML = html;
}
function dcPageClick(page, id) { currentPage = page; loadDischarges(); }
