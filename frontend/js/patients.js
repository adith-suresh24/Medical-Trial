let currentPage = 0;
const pageSize = 10;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadPatients();
    document.getElementById('searchPatient')?.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') loadPatients();
    });
});

async function loadPatients() {
    try {
        const search = document.getElementById('searchPatient')?.value || '';
        const status = document.getElementById('filterStatus')?.value || '';
        const params = { skip: currentPage * pageSize, limit: pageSize };
        if (search) params.search = search;
        if (status) params.status = status;

        const data = await api.getPatients(params);
        const patients = data.patients || data || [];
        const total = data.total || patients.length || 0;
        renderPatients(patients);
        renderPagination('patientsPagination', total, currentPage, pageSize, (page) => {
            currentPage = page;
            loadPatients();
        });
    } catch (err) {
        showToast('Failed to load patients: ' + err.message, 'error');
    }
}

function renderPatients(patients) {
    const tbody = document.getElementById('patientsTable');
    if (!Array.isArray(patients) || patients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding:40px">No patients found</td></tr>';
        return;
    }
    tbody.innerHTML = patients.map(p => `
        <tr>
            <td><strong>${p.patient_id}</strong></td>
            <td><a href="patient-detail.html?id=${p.id}">${p.first_name} ${p.last_name}</a></td>
            <td>${p.gender}</td>
            <td>${p.department || 'N/A'}</td>
            <td><span class="badge ${p.status === 'active' ? 'badge-success' : p.status === 'discharged' ? 'badge-secondary' : 'badge-warning'}">${p.status}</span></td>
            <td>${new Date(p.admission_date).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewPatient(${p.id})">View</button>
                <button class="btn btn-sm btn-warning" onclick="editPatient(${p.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deletePatient(${p.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function openAddPatient() {
    document.getElementById('patientModalTitle').textContent = 'Add New Patient';
    document.getElementById('patientForm').reset();
    document.getElementById('editPatientId').value = '';
    document.getElementById('patientModal').classList.add('active');
}

async function editPatient(id) {
    try {
        const patient = await api.getPatient(id);
        document.getElementById('patientModalTitle').textContent = 'Edit Patient';
        document.getElementById('editPatientId').value = patient.id;
        document.getElementById('firstName').value = patient.first_name;
        document.getElementById('lastName').value = patient.last_name;
        document.getElementById('dateOfBirth').value = patient.date_of_birth;
        document.getElementById('gender').value = patient.gender;
        document.getElementById('bloodGroup').value = patient.blood_group || '';
        document.getElementById('phone').value = patient.phone || '';
        document.getElementById('email').value = patient.email || '';
        document.getElementById('address').value = patient.address || '';
        document.getElementById('emergencyContact').value = patient.emergency_contact_name || '';
        document.getElementById('emergencyPhone').value = patient.emergency_contact_phone || '';
        document.getElementById('admissionReason').value = patient.admission_reason || '';
        document.getElementById('department').value = patient.department || '';
        document.getElementById('wardNumber').value = patient.ward_number || '';
        document.getElementById('bedNumber').value = patient.bed_number || '';
        document.getElementById('medicalHistory').value = patient.medical_history || '';
        document.getElementById('allergies').value = patient.allergies || '';
        document.getElementById('currentMedications').value = patient.current_medications || '';
        document.getElementById('patientModal').classList.add('active');
    } catch (err) {
        showToast('Failed to load patient: ' + err.message, 'error');
    }
}

async function viewPatient(id) {
    window.location.href = `patient-detail.html?id=${id}`;
}

async function savePatient() {
    const data = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        date_of_birth: document.getElementById('dateOfBirth').value,
        gender: document.getElementById('gender').value,
        blood_group: document.getElementById('bloodGroup').value || null,
        phone: document.getElementById('phone').value || null,
        email: document.getElementById('email').value || null,
        address: document.getElementById('address').value || null,
        emergency_contact_name: document.getElementById('emergencyContact').value || null,
        emergency_contact_phone: document.getElementById('emergencyPhone').value || null,
        admission_reason: document.getElementById('admissionReason').value || null,
        department: document.getElementById('department').value || null,
        ward_number: document.getElementById('wardNumber').value || null,
        bed_number: document.getElementById('bedNumber').value || null,
        medical_history: document.getElementById('medicalHistory').value || null,
        allergies: document.getElementById('allergies').value || null,
        current_medications: document.getElementById('currentMedications').value || null,
    };

    try {
        const editId = document.getElementById('editPatientId').value;
        if (editId) {
            await api.updatePatient(editId, data);
            showToast('Patient updated successfully', 'success');
        } else {
            await api.createPatient(data);
            showToast('Patient created successfully', 'success');
        }
        closeModal('patientModal');
        loadPatients();
    } catch (err) {
        showToast('Failed to save patient: ' + err.message, 'error');
    }
}

async function deletePatient(id) {
    if (!confirm('Are you sure you want to delete this patient? This action cannot be undone.')) return;
    try {
        await api.deletePatient(id);
        showToast('Patient deleted successfully', 'success');
        loadPatients();
    } catch (err) {
        showToast('Failed to delete patient: ' + err.message, 'error');
    }
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function renderPagination(containerId, total, current, size, onPage) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const totalPages = Math.ceil(total / size) || 1;
    if (totalPages <= 1) { container.innerHTML = ''; return; }

    let html = `<button ${current === 0 ? 'disabled' : ''} onclick="onPageClick(${current - 1}, '${containerId}')">‹</button>`;
    for (let i = 0; i < totalPages; i++) {
        if (i === 0 || i === totalPages - 1 || Math.abs(i - current) <= 2) {
            html += `<button class="${i === current ? 'active' : ''}" onclick="onPageClick(${i}, '${containerId}')">${i + 1}</button>`;
        } else if (Math.abs(i - current) === 3) {
            html += `<button disabled>...</button>`;
        }
    }
    html += `<button ${current >= totalPages - 1 ? 'disabled' : ''} onclick="onPageClick(${current + 1}, '${containerId}')">›</button>`;
    container.innerHTML = html;
}

function onPageClick(page, containerId) {
    currentPage = page;
    loadPatients();
}
