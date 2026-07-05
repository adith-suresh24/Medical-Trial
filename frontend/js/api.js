const API_BASE = 'http://localhost:8000/api';

const api = {
    getToken: () => localStorage.getItem('access_token'),
    setToken: (token) => localStorage.setItem('access_token', token),
    removeToken: () => localStorage.removeItem('access_token'),
    getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
    setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
    removeUser: () => localStorage.removeItem('user'),

    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        const token = this.getToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                this.removeToken();
                this.removeUser();
                window.location.href = '/frontend/pages/login.html';
            }
            throw error;
        }
    },

    get: (endpoint, params = {}) => {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return api.request(url, { method: 'GET' });
    },

    post: (endpoint, data) => api.request(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    put: (endpoint, data) => api.request(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),

    delete: (endpoint) => api.request(endpoint, {
        method: 'DELETE',
    }),

    // Auth
    login: (username, password) => api.post('/auth/login', { username, password }),
    logout: () => api.post('/auth/logout'),
    getMe: () => api.get('/auth/me'),
    register: (data) => api.post('/auth/register', data),
    changePassword: (data) => api.put('/auth/change-password', data),

    // Patients
    getPatients: (params) => api.get('/patients', params),
    getPatient: (id) => api.get(`/patients/${id}`),
    createPatient: (data) => api.post('/patients', data),
    updatePatient: (id, data) => api.put(`/patients/${id}`, data),
    deletePatient: (id) => api.delete(`/patients/${id}`),

    // Reports
    getReports: (params) => api.get('/reports', params),
    getReport: (id) => api.get(`/reports/${id}`),
    createReport: (data) => api.post('/reports', data),
    updateReport: (id, data) => api.put(`/reports/${id}`, data),
    deleteReport: (id) => api.delete(`/reports/${id}`),

    // Diagnosis
    getDiagnosisDatabase: (params) => api.get('/diagnosis/database', params),
    getPatientDiagnoses: (patientId) => api.get(`/diagnosis/patient/${patientId}`),
    createDiagnosis: (data) => api.post('/diagnosis', data),
    matchSymptoms: (data) => api.post('/diagnosis/match', data),

    // AI
    generateAISummary: (reportId) => api.post(`/ai/summarize/${reportId}`),

    // Discharge
    getDischargeReports: (params) => api.get('/discharge', params),
    createDischargeReport: (data) => api.post('/discharge', data),
    getDischargePDF: (id) => `${API_BASE}/discharge/${id}/download`,
    generateDischargePDF: (id) => api.post(`/discharge/${id}/generate-pdf`),

    // Logs
    getLogs: (params) => api.get('/logs', params),

    // Users
    getUsers: () => api.get('/auth/users'),
};
