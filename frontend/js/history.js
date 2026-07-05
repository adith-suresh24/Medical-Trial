document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    document.getElementById('historySearch')?.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') searchHistory();
    });
});

async function searchHistory() {
    const search = document.getElementById('historySearch')?.value.trim();
    if (!search) { showToast('Please enter a patient name or ID', 'warning'); return; }
    const resultsDiv = document.getElementById('historyResults');
    resultsDiv.innerHTML = '<div class="text-center" style="padding:40px"><div class="spinner" style="margin:0 auto"></div></div>';
    try {
        const data = await api.getPatients({ search, limit: 10 });
        const patients = data.patients || [];
        if (!patients.length) {
            resultsDiv.innerHTML = '<p class="text-center" style="padding:40px;color:var(--gray-500)">No patients found</p>';
            return;
        }
        let html = '';
        for (const patient of patients) {
            html += `<div class="card mb-2">
                <div class="flex-between mb-2">
                    <div>
                        <h3><a href="patient-detail.html?id=${patient.id}">${patient.first_name} ${patient.last_name}</a></h3>
                        <p style="color:var(--gray-500);font-size:13px">${patient.patient_id} | ${patient.gender} | ${patient.department || 'N/A'}</p>
                    </div>
                    <span class="badge ${patient.status === 'active' ? 'badge-success' : 'badge-secondary'}">${patient.status}</span>
                </div>
                <div id="history-${patient.id}">
                    <p style="color:var(--gray-500)">Loading history...</p>
                </div>
            </div>`;
            // Load history asynchronously
            loadPatientHistory(patient.id);
        }
        resultsDiv.innerHTML = html;
    } catch (err) {
        resultsDiv.innerHTML = `<p style="color:var(--danger)">Failed: ${err.message}</p>`;
    }
}

async function loadPatientHistory(patientId) {
    try {
        const [reportsData, diagnoses, dischargesData] = await Promise.all([
            api.getReports({ patient_id: patientId, limit: 100 }),
            api.getPatientDiagnoses(patientId),
            api.getDischargeReports({ patient_id: patientId, limit: 100 }),
        ]);
        const reports = reportsData.reports || [];
        const discharges = dischargesData.reports || [];
        const container = document.getElementById(`history-${patientId}`);
        if (!container) return;

        let html = '<div style="position:relative;padding-left:20px;border-left:2px solid var(--primary)">';

        // Admission
        html += `<div style="margin-bottom:16px;position:relative">
            <div style="position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--success);border:2px solid white"></div>
            <small style="color:var(--gray-500)">Admission</small>
            <p><strong>Admitted</strong> - Initial assessment</p>
        </div>`;

        // Reports
        reports.forEach(r => {
            html += `<div style="margin-bottom:12px;position:relative">
                <div style="position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--info);border:2px solid white"></div>
                <small style="color:var(--gray-500)">${new Date(r.created_at).toLocaleDateString()}</small>
                <p><strong>Medical Report</strong> - ${(r.symptoms || '').substring(0, 60)}...</p>
            </div>`;
        });

        // Diagnoses
        diagnoses.forEach(d => {
            html += `<div style="margin-bottom:12px;position:relative">
                <div style="position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--warning);border:2px solid white"></div>
                <small style="color:var(--gray-500)">${new Date(d.created_at).toLocaleDateString()}</small>
                <p><strong>Diagnosis</strong> - ${d.condition_name} (${d.severity || 'N/A'})</p>
            </div>`;
        });

        // Discharges
        discharges.forEach(d => {
            html += `<div style="margin-bottom:12px;position:relative">
                <div style="position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--danger);border:2px solid white"></div>
                <small style="color:var(--gray-500)">${d.discharge_date}</small>
                <p><strong>Discharge</strong> - ${(d.diagnosis || '').substring(0, 60)}...</p>
            </div>`;
        });

        if (!reports.length && !diagnoses.length && !discharges.length) {
            html += '<p style="color:var(--gray-500)">No history records found</p>';
        }

        html += '</div>';
        container.innerHTML = html;
    } catch (err) {
        const container = document.getElementById(`history-${patientId}`);
        if (container) container.innerHTML = '<p style="color:var(--danger)">Failed to load history</p>';
    }
}
