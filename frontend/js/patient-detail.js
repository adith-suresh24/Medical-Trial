let currentPatient = null;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadPatientDetail();
});

function getPatientId() {
    return new URLSearchParams(window.location.search).get('id');
}

async function loadPatientDetail() {
    const id = getPatientId();
    if (!id) {
        showToast('No patient ID specified', 'error');
        return;
    }
    try {
        const patient = await api.getPatient(id);
        currentPatient = patient;
        renderPatient(patient);
        loadPatientReports(id);
        loadPatientDiagnoses(id);
        loadPatientDischarges(id);
    } catch (err) {
        showToast('Failed to load patient: ' + err.message, 'error');
    }
}

function renderPatient(p) {
    document.getElementById('patientName').textContent = `${p.first_name} ${p.last_name}`;
    document.getElementById('patientId').textContent = `ID: ${p.patient_id} | ${p.status}`;

    document.getElementById('personalInfo').innerHTML = `
        <p><strong>DOB:</strong> ${p.date_of_birth} | <strong>Gender:</strong> ${p.gender}</p>
        <p><strong>Blood Group:</strong> ${p.blood_group || 'N/A'}</p>
        <p><strong>Phone:</strong> ${p.phone || 'N/A'} | <strong>Email:</strong> ${p.email || 'N/A'}</p>
        <p><strong>Address:</strong> ${p.address || 'N/A'}</p>
        <p><strong>Emergency:</strong> ${p.emergency_contact_name || 'N/A'} (${p.emergency_contact_phone || 'N/A'})</p>
        <p><strong>Medical History:</strong> ${p.medical_history || 'None'}</p>
        <p><strong>Allergies:</strong> ${p.allergies || 'None'}</p>
        <p><strong>Current Medications:</strong> ${p.current_medications || 'None'}</p>
    `;

    document.getElementById('admissionInfo').innerHTML = `
        <p><strong>Admission Date:</strong> ${new Date(p.admission_date).toLocaleDateString()}</p>
        <p><strong>Reason:</strong> ${p.admission_reason || 'N/A'}</p>
        <p><strong>Department:</strong> ${p.department || 'N/A'}</p>
        <p><strong>Ward:</strong> ${p.ward_number || 'N/A'} | <strong>Bed:</strong> ${p.bed_number || 'N/A'}</p>
    `;
}

async function loadPatientReports(patientId) {
    try {
        const data = await api.getReports({ patient_id: patientId });
        const reports = data.reports || [];
        const container = document.getElementById('patientReports');
        if (!reports.length) {
            container.innerHTML = '<p class="text-center" style="padding:20px;color:var(--gray-500)">No reports found</p>';
            return;
        }
        container.innerHTML = `<table><thead><tr><th>Date</th><th>Symptoms</th><th>Diagnosis</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>${reports.map(r => `<tr>
                <td>${new Date(r.created_at).toLocaleDateString()}</td>
                <td>${(r.symptoms || '').substring(0, 50)}...</td>
                <td>${r.diagnosis || 'Pending'}</td>
                <td><span class="badge ${r.is_finalized ? 'badge-success' : 'badge-warning'}">${r.is_finalized ? 'Finalized' : 'Draft'}</span></td>
                <td><button class="btn btn-sm btn-primary" onclick="window.location.href='reports.html?report_id=${r.id}'">View</button></td>
            </tr>`).join('')}</tbody></table>`;
    } catch (err) {
        document.getElementById('patientReports').innerHTML = '<p>Failed to load reports</p>';
    }
}

async function loadPatientDiagnoses(patientId) {
    try {
        const diagnoses = await api.getPatientDiagnoses(patientId);
        const container = document.getElementById('patientDiagnoses');
        if (!diagnoses.length) {
            container.innerHTML = '<p class="text-center" style="padding:20px;color:var(--gray-500)">No diagnoses recorded</p>';
            return;
        }
        container.innerHTML = `<table><thead><tr><th>Date</th><th>Condition</th><th>Severity</th><th>Status</th></tr></thead>
            <tbody>${diagnoses.map(d => `<tr>
                <td>${new Date(d.created_at).toLocaleDateString()}</td>
                <td>${d.condition_name}</td>
                <td><span class="badge ${d.severity === 'critical' ? 'badge-danger' : d.severity === 'high' ? 'badge-warning' : 'badge-info'}">${d.severity || 'N/A'}</span></td>
                <td><span class="badge ${d.is_confirmed ? 'badge-success' : 'badge-secondary'}">${d.is_confirmed ? 'Confirmed' : 'Pending'}</span></td>
            </tr>`).join('')}</tbody></table>`;
    } catch (err) {
        document.getElementById('patientDiagnoses').innerHTML = '<p>Failed to load diagnoses</p>';
    }
}

async function loadPatientDischarges(patientId) {
    try {
        const data = await api.getDischargeReports({ patient_id: patientId });
        const reports = data.reports || [];
        const container = document.getElementById('patientDischarges');
        if (!reports.length) {
            container.innerHTML = '<p class="text-center" style="padding:20px;color:var(--gray-500)">No discharge reports</p>';
            return;
        }
        container.innerHTML = `<table><thead><tr><th>Date</th><th>Diagnosis</th><th>PDF</th></tr></thead>
            <tbody>${reports.map(r => `<tr>
                <td>${r.discharge_date}</td>
                <td>${(r.diagnosis || '').substring(0, 60)}...</td>
                <td>${r.pdf_path ? `<a href="${api.getDischargePDF(r.id)}" class="btn btn-sm btn-success" download>📄 Download</a>` : 'Not generated'}</td>
            </tr>`).join('')}</tbody></table>`;
    } catch (err) {
        document.getElementById('patientDischarges').innerHTML = '<p>Failed to load discharges</p>';
    }
}

function editPatient() {
    if (currentPatient) window.location.href = `patients.html?edit=${currentPatient.id}`;
}

async function deletePatient() {
    if (!currentPatient || !confirm('Delete this patient permanently?')) return;
    try {
        await api.deletePatient(currentPatient.id);
        showToast('Patient deleted', 'success');
        window.location.href = 'patients.html';
    } catch (err) {
        showToast('Delete failed: ' + err.message, 'error');
    }
}
