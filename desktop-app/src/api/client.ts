import axios from 'axios';

const API_URL = 'http://localhost:8001/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

let currentAuthUser = '';
let currentAuthPin = '';

export const setAuth = (user: string, pin: string) => {
    currentAuthUser = user;
    currentAuthPin = pin;
};

api.interceptors.request.use((config) => {
    config.headers['x-auth-user'] = currentAuthUser;
    config.headers['x-auth-pin'] = currentAuthPin;
    return config;
});

// ─── Interfaces ──────────────────────────────────────────────

export interface Patient {
    id: number;
    name: string;
    date_of_birth?: string;
    gender?: string;
    blood_type?: string;
    allergies: string[];
    conditions: string[];
    cie10_codes: string[];
    contact_phone?: string;
    contact_email?: string;
    emergency_contact?: string;
    notes?: string;
    created_by?: string;
    created_at?: string;
    updated_at?: string;
}

export interface Vitals {
    blood_pressure?: string;
    heart_rate?: string;
    temperature?: string;
    weight?: string;
    height?: string;
    spo2?: string;
}

export interface Diagnosis {
    description: string;
    cie10_code?: string;
}

export interface Medication {
    drug_name: string;
    dose?: string;
    frequency?: string;
    duration?: string;
    instructions?: string;
}

export interface LabValue {
    test_name: string;
    value?: string;
    unit?: string;
    reference_range?: string;
    is_abnormal?: boolean;
}

export interface ConsultationAnalysis {
    patient_info?: { name?: string; age?: string; gender?: string };
    document_type?: string;
    subjective?: {
        chief_complaint?: string;
        symptoms?: string[];
        history?: string;
    };
    objective?: {
        vitals?: Vitals;
        findings?: string[];
    };
    assessment?: {
        diagnoses?: Diagnosis[];
        differential_diagnoses?: string[];
    };
    plan?: {
        medications?: Medication[];
        studies?: string[];
        referrals?: string[];
        follow_up?: string;
        recommendations?: string[];
    };
    lab_values?: LabValue[];
    summary?: string;
    confidence_score?: number;
    error?: string;
}

export interface Consultation {
    id: number;
    patient_id?: number;
    user_id: string;
    document_type: string;
    status: string;
    priority: string;
    summary: string;
    confidence_score: number;
    created_at?: string;
    reviewed_at?: string;
}

export interface ConsultationDetail extends Consultation {
    patient?: Patient;
    raw_text: string;
    image_path: string;
    ai_analysis: ConsultationAnalysis;
    prescriptions: Prescription[];
}

export interface Prescription {
    id: number;
    consultation_id: number;
    patient_id: number;
    drug_name: string;
    dose?: string;
    frequency?: string;
    duration?: string;
    instructions?: string;
    created_at?: string;
}

export interface LabResult {
    id: number;
    patient_id: number;
    consultation_id?: number;
    test_name: string;
    value?: string;
    unit?: string;
    reference_range?: string;
    is_abnormal: number;
    test_date?: string;
    created_at?: string;
}

export interface MedicalStats {
    total_patients: number;
    total_consultations: number;
    document_types: Record<string, number>;
    consultations_by_status: Record<string, number>;
}

// ─── Patients ────────────────────────────────────────────────

export const getPatients = async (): Promise<Patient[]> => {
    const response = await api.get('/patients');
    return response.data;
};

export const getPatient = async (id: number): Promise<Patient> => {
    const response = await api.get(`/patients/${id}`);
    return response.data;
};

export const createPatient = async (data: Omit<Patient, 'id' | 'created_at' | 'updated_at' | 'created_by'>): Promise<{ status: string; patient_id: number }> => {
    const response = await api.post('/patients', data);
    return response.data;
};

export const updatePatient = async (id: number, data: Partial<Patient>): Promise<void> => {
    await api.put(`/patients/${id}`, data);
};

export const deletePatient = async (id: number): Promise<void> => {
    await api.delete(`/patients/${id}`);
};

export const searchPatients = async (query: string): Promise<Patient[]> => {
    const response = await api.get(`/patients/search?q=${encodeURIComponent(query)}`);
    return response.data;
};

// ─── Consultations ───────────────────────────────────────────

export const getConsultations = async (): Promise<Consultation[]> => {
    const response = await api.get('/consultations');
    return response.data;
};

export const getConsultationDetail = async (id: number): Promise<ConsultationDetail> => {
    const response = await api.get(`/consultations/${id}`);
    return response.data;
};

export const createTextConsultation = async (text: string, patientId?: number): Promise<{ status: string; consultation_id: number }> => {
    const response = await api.post('/consultations/text', { text, patient_id: patientId });
    return response.data;
};

export const deleteConsultation = async (id: number): Promise<void> => {
    await api.delete(`/consultations/${id}`);
};

export const regenerateConsultation = async (id: number, rawText?: string): Promise<void> => {
    await api.post(`/consultations/${id}/regenerate`, { raw_text: rawText });
};

export const markReviewed = async (id: number): Promise<void> => {
    await api.post(`/consultations/${id}/review`);
};

export const linkPatient = async (consultationId: number, patientId: number): Promise<void> => {
    await api.post(`/consultations/${consultationId}/link-patient`, { patient_id: patientId });
};

// ─── Patient Data ────────────────────────────────────────────

export const getPatientConsultations = async (patientId: number): Promise<Consultation[]> => {
    const response = await api.get(`/patients/${patientId}/consultations`);
    return response.data;
};

export const getPatientPrescriptions = async (patientId: number): Promise<Prescription[]> => {
    const response = await api.get(`/patients/${patientId}/prescriptions`);
    return response.data;
};

export const getPatientLabResults = async (patientId: number): Promise<LabResult[]> => {
    const response = await api.get(`/patients/${patientId}/lab-results`);
    return response.data;
};

// ─── Documents ───────────────────────────────────────────────

export const downloadMedicalNote = async (consultationId: number): Promise<Blob> => {
    const response = await api.get(`/documents/medical-note/${consultationId}`, {
        responseType: 'blob'
    });
    return response.data;
};

export const downloadPrescription = async (consultationId: number): Promise<Blob> => {
    const response = await api.get(`/documents/prescription/${consultationId}`, {
        responseType: 'blob'
    });
    return response.data;
};

// ─── Upload & Capture ────────────────────────────────────────

export const uploadImage = async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
};

export const captureWebcam = async () => {
    const response = await api.post('/capture_webcam');
    return response.data;
};

// ─── Users ───────────────────────────────────────────────────

export const getUsers = async (): Promise<{ username: string; pin: string }[]> => {
    const response = await api.get('/users');
    return response.data;
};

export const createUser = async (username: string, pin: string): Promise<void> => {
    await api.post('/users', { username, pin });
};

export const deleteUser = async (username: string): Promise<void> => {
    await api.delete(`/users/${username}`);
};

// ─── Stats ───────────────────────────────────────────────────

export const getStats = async (): Promise<MedicalStats> => {
    const response = await api.get('/stats');
    return response.data;
};

export default api;
