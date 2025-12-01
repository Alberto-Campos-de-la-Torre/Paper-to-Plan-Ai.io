import axios from 'axios';

const API_URL = 'http://localhost:8001/api';

// Configure axios with base URL
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

let currentAuthUser = 'Beto May';
let currentAuthPin = '0295';

export const setAuth = (user: string, pin: string) => {
    currentAuthUser = user;
    currentAuthPin = pin;
};

api.interceptors.request.use((config) => {
    config.headers['x-auth-user'] = currentAuthUser;
    config.headers['x-auth-pin'] = currentAuthPin;
    return config;
});

export interface Note {
    id: number;
    title: string;
    status: string;
    implementation_time: string;
    feasibility_score: number;
    created_at?: string;
    raw_text?: string;
    summary?: string;
    technical_considerations?: string[];
    recommended_stack?: string[];
}

export const captureWebcam = async () => {
    const response = await api.post('/capture_webcam');
    return response.data;
};

export const getNotes = async (): Promise<Note[]> => {
    const response = await api.get('/notes');
    return response.data;
};

export const getNoteDetail = async (id: number): Promise<Note> => {
    const response = await api.get(`/notes/${id}`);
    return response.data;
};

export const uploadImage = async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return response.data;
};

export const getStats = async (): Promise<any> => {
    const response = await api.get('/stats');
    return response.data;
};

export const getUsers = async (): Promise<{ username: string, pin: string }[]> => {
    const response = await api.get('/users');
    return response.data;
};

export const deleteNote = async (id: number): Promise<void> => {
    await api.delete(`/notes/${id}`);
};

export const regenerateNote = async (id: number, newText: string): Promise<void> => {
    await api.post(`/notes/${id}/regenerate`, { raw_text: newText });
};

export const markCompleted = async (id: number): Promise<void> => {
    await api.post(`/notes/${id}/complete`);
};

export const createUser = async (username: string, pin: string): Promise<void> => {
    await api.post('/users', { username, pin });
};

export const deleteUser = async (username: string): Promise<void> => {
    await api.delete(`/users/${username}`);
};

export const updateConfig = async (config: { host: string, logic_model: string, vision_model: string }): Promise<void> => {
    await api.post('/config', config);
};

export const testConnection = async (): Promise<any> => {
    const response = await api.get('/config/test');
    return response.data;
};

export const createTextNote = async (text: string): Promise<void> => {
    await api.post('/notes/text', { text });
};

export default api;
